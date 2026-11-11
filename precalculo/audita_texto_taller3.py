#!/usr/bin/env python3
"""
audita_texto_taller3.py — la prosa del Taller 3, y lo que viaja con ella

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_3_SIG.md.

Mismo núcleo que los auditores de prosa de los capítulos y de los Talleres 1
y 2 —`audita_texto_base`—, con el mismo criterio del Taller 2: forzar a un
taller a pasar las comprobaciones de un capítulo es peor que no hacerlas,
porque se aprueban por vacuidad y el informe queda verde sobre algo que nadie
miró. Se declara qué NO se llama:

  · `cifras()` — compara cada número de la prosa contra un ÍNDICE de todo lo
    que el JSON y sus razones, diferencias y porcentajes permiten escribir.
    Aquí no hay precálculo que citar: el taller no da ningún resultado, y el
    JSON publicado (1000 variantes y 16 fichas de n, área y lambda) mete en
    ese índice cientos de cifras que no son respuesta de nada. Un número
    inventado de pocos decimales cae dentro por azar —es el punto ciego que
    `mide_punto_ciego.py` cuantificó en los capítulos—. Se sustituye por algo
    MÁS ESTRICTO y más simple: una lista CERRADA de constantes de diseño
    (fechas, pesos, valores que QGIS recibe, códigos de proyección, versiones
    del armazón). Todo número de la prosa que no sea un entero chico y no
    esté en la lista es una cifra que alguien escribió sin que el taller lo
    prometiera. Medido el 2026-11-11: 47 números distintos en la prosa, 0 sin
    lista; y un «0.85» o un «1.4» inventados caen.

  · `accesibilidad()` — exige al menos un bloque de autoevaluación, y este
    taller no lleva quiz. Lo que sí aplica (los plegables con `aria-expanded`
    y `aria-controls`) se comprueba aquí abajo, a mano. Los lienzos no
    existen en el marcado: los simuladores del motor no se usan.

  · `geomapas()` — el taller no publica mapas: el mapa lo hace el estudiante en
    QGIS. · `soluciones()` — no hay solucionario: esa fue la decisión.
  · `fuentes()` — las referencias son las del armazón de la plantilla, no del
    taller.

LO QUE SÍ COMPRUEBA, Y ES LO PROPIO DE ESTE TALLER

  1. EL CALENDARIO, UNO SOLO. La fecha y la hora que dice la página son las
     constantes `ENTREGA` y `HORA_LIMITE` de `ensambla_taller3.py` —leídas
     del texto del archivo, no importadas, que el ensamblador arma la página
     al importarse— y las macros `\\fechaentrega` y `\\horalimite` del .tex, y
     lo que dice el PDF compilado si hay `pdftotext`. Son cuatro superficies
     que publican lo mismo y cada una tiene una copia a mano.

  2. LO QUE SE DESCARGA. Cada `href="../entrega/..."` existe; la página
     enlaza los cinco archivos del taller; el ZIP del complemento lleva
     EXACTAMENTE los mismos bytes que la carpeta (un ZIP viejo reparte una
     herramienta que ya no es la que calculó las claves); y la huella de los
     datos que imprime la página es la del GeoPackage que se entrega.

  3. LAS HERRAMIENTAS. Cada identificador `native:…` o `qgis:…` que nombra la
     página es uno de los que usó `claves_qgis_taller3.py` —o el que la clave
     no usa, `native:basicstatisticsforfields`, que la prosa declara—, y al
     revés: toda herramienta con la que se calcularon las claves está en la
     página. Los nombres de las cuatro herramientas del complemento son los
     de su `displayName()`: el estudiante las busca por lo que lee en
     pantalla.

  4. LOS PARÁMETROS. Lo que el enunciado manda poner a QGIS (radio máximo, paso,
     simulaciones, semilla, sitios por lado, píxel, lado de las rejillas) es lo
     que corrió el script de las claves. Si uno se mueve y el otro no, las
     cifras de control dejan de ser las que el estudiante obtiene.

  5. QUE LA PÁGINA NO CONTENGA NINGUNA RESPUESTA. Tres superficies vigilan
     esto: `audita_taller3.py` mira el JSON, `ensambla_taller3.py` mira su
     propia salida antes de escribirla, y este mira el texto YA ensamblado
     que el estudiante lee: las frases que adelantan el sentido de un
     resultado, los nombres de campo de las claves, los comentarios del
     bloque de R —que no se leen como prosa y por eso Taller 2 destapó ahí su
     única filtración—, y, si las claves están, que NINGUNA cifra de control
     aparezca escrita en la página.

  6. LA ESTRUCTURA. Los cinco pesos suman 100 y son los mismos en las
     cinco tareas, en la tabla del módulo 7 y en el ensamblador; la rúbrica
     suma 100; hay siete módulos, los de la navegación y los de las plantillas, con
     el mismo título; la tira de variante está en los seis primeros; el .tex
     trae un marcador por cada lectura que pide el enunciado.

EL TOPE DE PESO, Y SU ARITMÉTICA
Como en el Taller 2, el tope es una cota con dos extremos. Por abajo, el
tamaño de hoy: **431 KB**, de los que **93** son el JSON incrustado (el
buscador lo necesita entero) y el resto el motor de la plantilla y la prosa
propia. Por arriba, la ceguera del arnés: `prueba_texto.py` tumba esta
comprobación inyectando **+312 KB** de comentario, y si el tope pasara de
431 + 312 = **743 KB** la inyección ya no lo rebasaría. **520 KB** deja 89 KB
de crecimiento y se queda 223 KB por debajo del punto ciego. Si el taller se
acerca a 520 hay que revisar el número Y la inyección, no solo el número.
NOTA: `prueba_texto.py` todavía no conoce este documento (su tabla `DOCUMENTOS`
trae `taller2` y no `taller3`); hasta que alguien lo añada, la cota la vigila
esta aritmética y no el arnés.

Uso:  cd precalculo && python3 audita_texto_taller3.py
Devuelve 1 si algo falla. TALLER3_HTML, TALLER3_TEX y TALLER3_ZIP apuntan a copias con
defectos (el JSON, las claves y los datos entregados no se redirigen aquí).
"""
from __future__ import annotations

import ast
import hashlib
import html
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from audita_texto_base import Auditor  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
ENTREGA_DIR = RAIZ / "entrega"
CACHE = PRECALCULO / "cache"

# El tope propio. La aritmética que lo sostiene está en la cabecera.
TOPE_KB_TALLER3 = 520.0

# Los cinco archivos que el enunciado manda descargar.
DESCARGAS = {"entrega/qgis/taller3_espacial.zip", "entrega/datos/taller3.gpkg",
             "entrega/datos/taller3_sedes_3857.geojson", "entrega/plantilla_taller3.tex",
             "entrega/plantilla_taller3.pdf"}

# Lo que el taller NO puede decir. Las once primeras son las de `ensambla_taller3.py` (la
# primera superficie, copiadas aquí A PROPÓSITO: son la segunda contra la que se coteja);
# las cuatro últimas las añade este auditor, y adelantan el SENTIDO de un resultado.
PROHIBIDAS = [
    "tu patrón está agregado", "tu patrón es aleatorio", "tu patrón es regular",
    "tu índice sube", "tu índice baja", "queda fuera de la banda", "queda dentro de la banda",
    "indice_qgis", "l_menos_r", "pct_fuera", "bw_diggle",
    "el índice de vecino más próximo sube", "el índice de vecino más próximo baja",
    "queda por encima de la banda", "queda por debajo de la banda",
]

# Los nombres de campo de las claves: si uno aparece en la página, se coló un trozo de una clave.
# No están `pico_sin`, `masa_sin`, `pico_con`, `masa_con` ni `radio_qgis`: son los nombres de lo que
# imprime el BLOQUE DE R del enunciado, y deben estar.
LLAVES_DE_RESPUESTA = [
    "p_derecha", "p_bilateral", "esperado_min", "esperada_qgis", "esperada_area_real",
    "indice_area_real", "area_caja_km2", "z_qgis", "masa_dentro", "masa_total", "suma_dentro",
    "usables", "banda_inf", "banda_sup", "inflacion_pct", "area_3857_km2", "cambian_de_clase",
    "puesto_conteo", "puesto_densidad", "clase_cuantiles", "clase_jenks", "cortes_jenks",
    "cortes_cuantiles", "reetiquetadas_dentro", "radio_qgis_diggle", "radio_qgis_ppl",
    "ppl_en_el_limite", "bw_ppl", "sedes_contadas", "media_ocupadas",
]

# Las constantes de DISEÑO que la prosa puede escribir sin que sean un resultado. Los enteros
# del 0 al 12 pasan sin lista (como en la base: el material cuenta módulos y capítulos); lo
# demás tiene que estar aquí o en `permitidas()`, que las saca de donde viven.
CONSTANTES = {
    # Lo que se le manda poner a QGIS: paso de r, píxel, simulaciones, radio máximo, lados de
    # las rejillas; todo cotejado contra el script de las claves en `parametros()`.
    "25", "50", "99", "1000", "2000", "4000",
    # Una latitud de la pregunta T1(c): «una ciudad a 60° de latitud».
    "60",
    # La fórmula de la distancia esperada: 0,5 / sqrt(n / A).
    "0.5",
    # Códigos de proyección y de la asignatura.
    "9377", "3857", "20929",
    # El armazón de la plantilla: años de las referencias y de los CDN, y la licencia
    # «CC BY-NC-ND 4.0» del libro de Moraga.
    "1993", "2011", "2013", "2014", "2015", "2019", "2023", "4.0",
}


def lee(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def constantes_del_ensamblador():
    """(ENTREGA, HORA_LIMITE, QGIS_VERSION, PESOS) leídos del TEXTO de `ensambla_taller3.py`."""
    src = lee(PRECALCULO / "ensambla_taller3.py")

    def cadena(nombre):
        m = re.search(rf'^{nombre}\s*=\s*"([^"]*)"', src, re.M)
        return m.group(1) if m else None

    m = re.search(r"^PESOS\s*=\s*(\{[^}]*\})", src, re.M)
    try:
        pesos = ast.literal_eval(m.group(1)) if m else None
    except (ValueError, SyntaxError):
        pesos = None
    return cadena("ENTREGA"), cadena("HORA_LIMITE"), cadena("QGIS_VERSION"), pesos


def parametros_del_script():
    """Lo que `claves_qgis_taller3.py` le pasó a QGIS, leído del texto del script."""
    s = lee(PRECALCULO / "claves_qgis_taller3.py")
    p = {}
    m = re.search(r"RMAX=(\d+),\s*PASO=(\d+),\s*LADO=(\d+)", s)
    p["gfj"] = tuple(int(x) for x in m.groups()) if m else None
    m = re.search(r"RMAX=(\d+),\s*PASO=(\d+),\s*NSIM=(\d+),\s*SEMILLA=(\d+)", s)
    p["ripley"] = tuple(int(x) for x in m.groups()) if m else None
    m = re.search(r"PIXEL_SIZE=(\d+)", s)
    p["pixel"] = int(m.group(1)) if m else None
    m = re.search(r"for lado in \(([\d,\s]+)\)", s)
    p["rejillas"] = tuple(int(x) for x in re.findall(r"\d+", m.group(1))) if m else None
    p["ids"] = set(re.findall(r'"((?:native|qgis|taller3):[a-z0-9_]+)"', s))
    return p


def permitidas(D, pesos, entrega, hora, qgis):
    """Las constantes de diseño, sacadas de donde viven y no escritas dos veces."""
    p = set(CONSTANTES)
    p |= {str(v) for v in (pesos or {}).values()} | {str(sum((pesos or {}).values()))}
    p |= set(re.findall(r"\d+", entrega or "")) | set(re.findall(r"\d+", hora or ""))
    p |= {".".join((qgis or "").split(".")[:2])}
    if isinstance(D, dict):
        for lst in (D.get("opciones") or {}).values():
            p |= {str(x) for x in lst}
        for k in ("sedes", "localidades"):
            p.add(str(((D.get("ciudad") or {}).get(k))))
        p |= {str(D.get("semilla")), str(D.get("n_min"))}
    return p


def hojas_flotantes(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from hojas_flotantes(v)
    elif isinstance(o, list):
        for v in o:
            yield from hojas_flotantes(v)
    elif isinstance(o, float) and o == o:
        yield o


def main() -> int:
    a = Auditor(capitulo="taller-3-sig-caps-1-5.html", var_entorno="TALLER3_HTML", jsons=[])
    saltadas: list[str] = []

    def salta(que, motivo):
        saltadas.append(f"{que} — {motivo}")
        print(f"  ···  {que:<62} SALTADA: {motivo}")

    import json
    ruta_d = pathlib.Path(os.environ.get("TALLER3_DATOS") or (PRECALCULO / "salidas" / "taller3_datos.json"))
    try:
        D = json.loads(lee(ruta_d))
    except json.JSONDecodeError:
        D = {}
    ENTREGA, HORA, QGIS_V, PESOS = constantes_del_ensamblador()
    script = parametros_del_script()

    # =================================================================
    print("\n=== El calendario, uno solo ===============================")
    a.exige(None not in (ENTREGA, HORA, QGIS_V) and isinstance(PESOS, dict),
            "se leen las constantes del ensamblador",
            f"{ENTREGA} · {HORA} · QGIS {QGIS_V} · pesos {PESOS}")
    plano = re.sub(r"\s+", " ", a.texto_plano)
    fechas = re.findall(r"\b(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo) \d{1,2} de "
                        r"[a-záéíóú]+(?: de \d{4})?", plano)
    a.exige(len(fechas) >= 2 and set(fechas) == {(ENTREGA or "?").lower()},
            "toda fecha de la página es la ENTREGA del ensamblador",
            f"{len(fechas)} fechas: {sorted(set(fechas))}")
    horas = re.findall(r"\b\d{1,2}:\d{2}\b", plano)
    a.exige(len(horas) >= 2 and set(horas) == {HORA},
            "toda hora de la página es la HORA_LIMITE del ensamblador",
            f"{len(horas)} horas: {sorted(set(horas))}")
    frase = re.escape((ENTREGA or "?").lower()) + r",? a más tardar a las " + re.escape(HORA or "?")
    a.exige(len(re.findall(frase, plano)) >= 2, "el enunciado da la entrega y la hora juntas, al menos dos veces",
            f"{len(re.findall(frase, plano))} veces")
    tex_ruta = pathlib.Path(os.environ.get("TALLER3_TEX") or (ENTREGA_DIR / "plantilla_taller3.tex"))
    tex = lee(tex_ruta)
    a.exige(tex_ruta.exists(), "la plantilla de entrega existe", tex_ruta.name)
    a.exige(f"\\newcommand{{\\fechaentrega}}{{{ENTREGA}}}" in tex,
            "la macro \\fechaentrega del .tex es la ENTREGA", str(ENTREGA))
    a.exige(f"\\newcommand{{\\horalimite}}{{{HORA}}}" in tex,
            "la macro \\horalimite del .tex es la HORA_LIMITE", str(HORA))
    otras = [m for m in re.findall(r"\b\d{1,2}:\d{2}\b", tex) if m != HORA]
    otras += [m for m in re.findall(r"\b\d{1,2} de (?:noviembre|diciembre|octubre)\b", tex)
              if m not in (ENTREGA or "")]
    a.exige(not otras, "el .tex no escribe a mano otra fecha ni otra hora", str(otras[:3]))
    pdf = ENTREGA_DIR / "plantilla_taller3.pdf"
    if shutil.which("pdftotext") and pdf.exists():
        txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        txt = re.sub(r"\s+", " ", txt)
        a.exige((ENTREGA or "?") in txt and (HORA or "?") in txt,
                "el PDF compilado de la plantilla dice la misma fecha y hora",
                "" if (ENTREGA or "?") in txt else "el PDF está desfasado respecto al .tex")
    else:
        salta("el PDF compilado de la plantilla", "no hay `pdftotext` o no existe el PDF")

    # =================================================================
    print("\n=== Lo que se descarga ====================================")
    hrefs = sorted(set(re.findall(r'href="\.\./(entrega/[^"]+)"', a.cuerpo)))
    a.exige(bool(hrefs), "la página enlaza archivos de entrega/", f"{len(hrefs)} enlaces")
    rotos = [h for h in hrefs if not (RAIZ / h).is_file()]
    a.exige(not rotos, "todo href=\"../entrega/…\" apunta a un archivo que existe", str(rotos))
    a.exige(DESCARGAS <= set(hrefs), "la página enlaza los cinco archivos del taller",
            f"faltan {sorted(DESCARGAS - set(hrefs))}")
    a.enlaces()

    carpeta = ENTREGA_DIR / "qgis" / "taller3_espacial"
    zip_ruta = pathlib.Path(os.environ.get("TALLER3_ZIP") or (ENTREGA_DIR / "qgis" / "taller3_espacial.zip"))
    en_carpeta = {f"taller3_espacial/{p.relative_to(carpeta).as_posix()}": p.read_bytes()
                  for p in carpeta.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                  and p.suffix != ".pyc"}
    if zip_ruta.exists():
        with zipfile.ZipFile(zip_ruta) as z:
            en_zip = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
    else:
        en_zip = {}
    a.exige(set(en_zip) == set(en_carpeta) and bool(en_zip),
            "el ZIP del complemento lleva los mismos archivos que la carpeta",
            f"difieren {sorted(set(en_zip) ^ set(en_carpeta))}")
    viejos = sorted(n for n in set(en_zip) & set(en_carpeta) if en_zip[n] != en_carpeta[n])
    a.exige(not viejos, "y cada uno con los mismos bytes: el ZIP no está viejo", f"distintos: {viejos}")
    gpkg = ENTREGA_DIR / "datos" / "taller3.gpkg"
    huella = hashlib.sha256(gpkg.read_bytes()).hexdigest()[:12] if gpkg.exists() else "?"
    huellas = re.findall(r"datos ([0-9a-f]{12})", a.texto_con_codigo)
    a.exige(bool(huellas) and set(huellas) == {huella}, "la huella de los datos de la página es la del GeoPackage",
            f"{huella} frente a {sorted(set(huellas))}")
    meta = lee(carpeta / "metadata.txt")
    alg = lee(carpeta / "algoritmos.py")
    v_meta = re.search(r"^version=(\S+)", meta, re.M)
    v_alg = re.search(r'^VERSION = "([^"]+)"', alg, re.M)
    a.exige(bool(v_meta) and bool(v_alg) and v_meta.group(1) == v_alg.group(1),
            "la versión del complemento (metadata.txt) es la de su código",
            f"{v_meta.group(1) if v_meta else '?'} frente a {v_alg.group(1) if v_alg else '?'}")

    # =================================================================
    print("\n=== Las herramientas ======================================")
    ids_pagina = set(re.findall(r"\b(?:native|qgis|taller3|gdal|grass7|processing):[a-z0-9_]+", a.doc))
    usados = script["ids"]
    permitidos = usados | {"native:basicstatisticsforfields"}
    a.exige(bool(ids_pagina) and ids_pagina <= permitidos,
            "todo identificador que nombra la página lo usó el script de las claves",
            f"{len(ids_pagina)} ids; sobran {sorted(ids_pagina - permitidos)}")
    faltan = sorted(i for i in usados if not i.startswith("taller3:") and i not in ids_pagina)
    a.exige(not faltan, "y toda herramienta nativa de las claves está en la página", f"faltan {faltan}")
    nombres = re.findall(r'def displayName\(self\):\s*return "([^"]+)"', alg)
    a.exige(len(nombres) == 4 and [n.split(" ")[0] for n in nombres] == ["0", "1", "2", "3"],
            "el complemento tiene cuatro herramientas, numeradas del 0 al 3", str([n[:12] for n in nombres]))
    ausentes = [n for n in nombres if n.lower() not in a.texto_plano]
    a.exige(not ausentes, "la página nombra cada herramienta como sale en pantalla", str(ausentes))
    prov = re.search(r'def name\(self\):\s*return "([^"]+)"', lee(carpeta / "proveedor.py"))
    a.exige(bool(prov) and prov.group(1).lower() in a.texto_plano,
            "y el grupo de la caja de herramientas, con su nombre", prov.group(1) if prov else "?")
    for palabra in ("cuártico", "escalado", "rectángulo (polígono)", "interseca"):
        a.exige(palabra in a.texto_plano, f"la página manda elegir «{palabra}»")

    # =================================================================
    print("\n=== Lo que se le manda poner a QGIS, y lo que corrió la clave ===")
    gfj = re.search(r"radio máximo (\d+), paso (\d+), sitios por lado (\d+)", plano)
    a.exige(gfj is not None and tuple(map(int, gfj.groups())) == script["gfj"],
            "G, F y J: radio máximo, paso y sitios por lado",
            f"página {gfj.groups() if gfj else None} frente al script {script['gfj']}")
    rip = re.search(r"radio máximo (\d+), paso (\d+), (\d+) simulaciones, semilla (\d+)", plano)
    a.exige(rip is not None and tuple(map(int, rip.groups())) == script["ripley"],
            "K y L: radio máximo, paso, simulaciones y semilla",
            f"página {rip.groups() if rip else None} frente al script {script['ripley']}")
    pix = re.search(r"tamaño de píxel x e y, (\d+)", plano)
    a.exige(pix is not None and int(pix.group(1)) == script["pixel"], "mapa de calor: tamaño de píxel",
            f"página {pix.group(1) if pix else None} frente al script {script['pixel']}")
    lados = tuple(int(x) for x in re.findall(r"espaciado horizontal y vertical, (\d+) metros", plano)
                  + re.findall(r"repite con (\d+)", plano))
    a.exige(lados == script["rejillas"], "las rejillas: lado de cada una",
            f"página {lados} frente al script {script['rejillas']}")
    a.exige(isinstance(D, dict) and D.get("semilla") == (script["ripley"] or (0, 0, 0, None))[3],
            "la semilla del JSON es la de la envolvente de las claves")

    # =================================================================
    print("\n=== Que la prosa no contenga ninguna respuesta ============")
    for frase_p in PROHIBIDAS:
        a.exige(frase_p not in a.texto_plano, f"la prosa no dice «{frase_p}»")
    doc_min = a.doc.lower()
    en_doc = [p for p in PROHIBIDAS if p in doc_min]
    a.exige(not en_doc, "ni el documento entero, scripts y JSON incluidos", str(en_doc))
    llaves = [k for k in LLAVES_DE_RESPUESTA if k in doc_min]
    a.exige(not llaves, "ningún nombre de campo de las claves aparece en el documento", str(llaves))

    # LOS COMENTARIOS DEL CÓDIGO SON PROSA, Y `texto_plano` NO LOS LEE (quita los <pre> y los <code>):
    # es la familia que destapó el Taller 2, y aquí el bloque de R es lo único que el taller escribe.
    bloques = re.findall(r'<code class="language-(?:r|python)[^"]*">(.*?)</code>', a.cuerpo, re.S)
    lineas = []
    for src in bloques:
        for ln in html.unescape(re.sub(r"<[^>]+>", "", src)).splitlines():
            m = re.search(r"#(.*)$", ln)
            if m and not ln.strip().startswith("#>"):
                lineas.append(m.group(1).strip())
    coment = " · ".join(lineas).lower()
    a.exige(len(bloques) >= 1 and len(lineas) >= 5, "se leen los comentarios del bloque de R",
            f"{len(bloques)} bloque(s) · {len(lineas)} comentarios")
    for frase_p in PROHIBIDAS:
        a.exige(frase_p not in coment, f"ningún comentario dice «{frase_p}»")
    codigo = "\n".join(re.sub(r"#.*$", "", ln)
                       for src in bloques for ln in html.unescape(re.sub(r"<[^>]+>", "", src)).splitlines())
    for llamada in ("Fest(", "distmap("):
        a.exige(llamada not in codigo, f"el bloque de R no llama a `{llamada}`  (M-14)")

    # Toda cifra de la prosa es una constante de diseño: la lista cerrada que sustituye a `cifras()`.
    ok_cifras = permitidas(D, PESOS, ENTREGA, HORA, QGIS_V)
    raras = sorted({c.replace(",", ".") for c in a.crudos
                    if c.replace(",", ".") not in ok_cifras
                    and not ("." not in c and len(c) <= 2 and int(c) <= 12)
                    and c != "00"})
    a.exige(len(a.crudos) > 100 and not raras, "toda cifra de la prosa es una constante de diseño",
            f"{len(a.crudos)} cifras leídas · SIN LISTA: {raras[:12]}" if raras else f"{len(a.crudos)} cifras leídas")

    # Y la comprobación más fuerte, que necesita las claves (no están en git): que NINGUNA cifra de
    # control aparezca escrita en la página. Se buscan las de cuatro decimales con cinco cifras
    # significativas, y a la página se le quita el JSON incrustado, que SÍ trae lo público.
    claves = {}
    for nombre in ("taller3_claves_qgis_mac.json", "taller3_claves_qgis_linux.json", "taller3_claves_r.json"):
        var = {"taller3_claves_qgis_mac.json": "TALLER3_CLAVES_MAC", "taller3_claves_qgis_linux.json":
               "TALLER3_CLAVES_LINUX", "taller3_claves_r.json": "TALLER3_CLAVES_R"}[nombre]
        p = pathlib.Path(os.environ.get(var) or (CACHE / nombre))
        if p.exists():
            try:
                claves[nombre] = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
    if not claves:
        salta("ninguna cifra de control escrita en la página",
              "SALTADO: no hay claves en precalculo/cache/ (no están en git); solo corre la lista de frases")
    else:
        resto = re.sub(r"const DATOS_T3 = .*", "", a.doc)
        en_pagina = set(re.findall(r"\d+\.\d{4,}", resto))
        cand = {}
        for nombre, obj in claves.items():
            for x in hojas_flotantes(obj):
                s = f"{abs(x):.4f}"
                cifras_sig = s.replace(".", "").lstrip("0")
                if abs(x) >= 0.01 and not s.endswith("0") and len(cifras_sig) >= 5:
                    cand.setdefault(s, nombre)
        filtradas = sorted(f"{s} ({n.split('_')[2].split('.')[0]})" for s, n in cand.items()
                           if any(t.startswith(s) for t in en_pagina))
        a.exige(not filtradas, "ninguna cifra de control de las claves aparece en la página",
                f"{len(cand)} cifras buscadas en {len(claves)} clave(s)" + (f" · FILTRADAS: {filtradas[:6]}" if filtradas else ""))

    # =================================================================
    a.afirmaciones([
        ("dice que el SIG se escribe y que un clic no deja rastro", "un clic no deja rastro"),
        ("dice que cuenta como uno de los quices del Corte III", "uno de los quices del corte iii"),
        ("dice que no se aceptan entregas tarde", "no se aceptan entregas tarde"),
        ("dice que la pertenencia es geométrica", "la pertenencia es geométrica"),
        ("manda poner el elipsoide en Ninguno/Planimétrico", "ninguno/planimétrico"),
        ("dice que la clase se lee con el límite superior dentro de ella", "el límite superior pertenece a la clase"),
        ("pide la bitácora y dice qué pasa sin ella", "bitácora"),
        ("dice que se puede usar IA sin pedir permiso", "sin pedir permiso"),
        ("advierte de que un modelo no puede dar las cifras de control", "un modelo no puede darte tus cifras de control"),
        ("declara la regla de las tres cifras significativas", "tres primeras cifras significativas"),
        ("dice qué corrección de borde usan las herramientas propias", "muestra reducida"),
        ("dice cómo se escribe un valor p muy pequeño", "notación científica"),
        ("dice qué pasa si se resuelve una variante ajena", "si resuelves una variante que no es la tuya"),
        ("dice que la ventana es el polígono y no su caja", "la ventana es el polígono de tu localidad"),
    ])
    a.temario([
        ("T1 · reproyectar frente a reetiquetar", "reproyectar no es reetiquetar"),
        ("T1 · qué es lo aleatorio en cada capa", "qué es lo aleatorio"),
        ("T2 · el esquema de clases decide el mapa", "rupturas naturales (jenks)"),
        ("T2 · las rejillas de 2 y 4 km (el MAUP)", "crear cuadricula"),
        ("T3 · el área que usa el vecino más próximo", "análisis de vecinos más próximos"),
        ("T3 · la banda de simulaciones y el r fijado de antemano", "r fijado de antemano"),
        ("T4 · el radio no es σ", "no son el mismo número"),
        ("T4 · la corrección de borde del mapa de calor", "corrección de borde"),
        ("T5 · los selectores de ancho de banda que QGIS no trae", "un selector de ancho de banda"),
        ("la rúbrica del taller", "taller3"),
    ])

    # =================================================================
    print("\n=== La estructura: pesos, módulos y tareas ================")
    pesos_pagina = [int(x) for x in re.findall(r'class="badge-peso">(\d+)&nbsp;%', a.cuerpo)]
    esperados = [PESOS[k] for k in sorted(PESOS)] if isinstance(PESOS, dict) else []
    a.exige(pesos_pagina == esperados and sum(esperados) == 100,
            "los pesos de las cinco tareas son los del ensamblador y suman 100", f"{pesos_pagina} → {sum(pesos_pagina)}")
    m7 = re.search(r'<template id="module-7">(.*?)</template>', a.doc, re.S)
    tabla = [int(x) for x in re.findall(r"<td>(\d+)&nbsp;%</td>", m7.group(1))] if m7 else []
    a.exige(tabla == esperados, "y la tabla del módulo 7 dice los mismos", str(tabla))
    rub = re.search(r"RUBRICAS\['taller3'\] = \{(.*?)\n    \};", a.doc, re.S)
    pts = [int(x) for x in re.findall(r"puntos: (\d+)", rub.group(1))] if rub else []
    a.exige(len(pts) >= 2 and sum(pts) == 100, "las dimensiones de la rúbrica suman 100", str(pts))
    ids = [int(x) for x in re.findall(r'<template id="module-(\d+)">', a.doc)]
    a.exige(ids == list(range(1, 8)), "hay siete plantillas de módulo, del 1 al 7", str(ids))
    nav = re.findall(r'\{ id: (\d+), title: "([^"]+)", duration: "[^"]+" \}', a.doc)
    a.exige([int(i) for i, _ in nav] == list(range(1, 8)), "la navegación declara los mismos siete módulos", str([i for i, _ in nav]))
    trozos = dict(zip(ids, re.split(r'<template id="module-\d+">', a.doc)[1:]))
    def h2_de(t):
        m = re.search(r"<h2[^>]*>(.*?)</h2>", t, re.S)
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""

    # EL h2, no el módulo entero: «Calificación» está en cualquier párrafo de la rúbrica y una
    # búsqueda por todo el texto daba verde con un título que ya no era el del módulo.
    malos = [i for i, t in nav if not h2_de(trozos.get(int(i), "")).startswith(html.unescape(t))]
    a.exige(not malos, "cada título de la navegación abre el h2 de su módulo", f"sin título: {malos}")
    con_tira = sorted(k for k, t in trozos.items() if 'data-simulador="taller3-variante"' in t)
    a.exige(con_tira == [1, 2, 3, 4, 5, 6], "la tira de variante está en los módulos 1 a 6 y no en el 7", str(con_tira))
    n_tareas = a.cuerpo.count('<div class="ejercicio-guiado">')
    a.exige(n_tareas == 5, "hay cinco tareas", str(n_tareas))
    a.exige('class="ejercicio-panel solucion"' not in a.cuerpo, "ninguna tarea lleva panel de solución")
    # El .tex trae un marcador por cada LECTURA que pide el enunciado, tarea por tarea.
    tareas = re.split(r'<div class="ejercicio-guiado">', a.cuerpo)[1:]
    lecturas = [t.split('<div class="ejercicio-acciones">')[0].count("frase-control") for t in tareas]
    secciones = re.split(r"\\section\{", tex)[1:]
    marcadores = [s.count("\\marcador{") for s in secciones]
    a.exige(len(lecturas) == len(marcadores) and lecturas == marcadores,
            "el .tex trae un marcador por cada lectura de cada tarea", f"página {lecturas} frente al .tex {marcadores}")

    # =================================================================
    print("\n=== Accesibilidad de lo que este documento sí tiene =======")
    botones = re.findall(r'<button[^>]*class="(?:derivacion|ejercicio)-boton"[^>]*>', a.cuerpo)
    a.exige(len(botones) >= 5 and all("aria-expanded" in b and "aria-controls" in b for b in botones),
            "los plegables declaran aria-expanded y aria-controls", f"{len(botones)} botones")
    huerfanos = [m for b in botones for m in re.findall(r'aria-controls="([^"]+)"', b) if f'id="{m}"' not in a.cuerpo]
    a.exige(not huerfanos, "y cada uno apunta a un panel que existe", str(huerfanos))
    lienzos = re.findall(r"<canvas[^>]*>", a.cuerpo)
    a.exige(all("aria-label" in c for c in lienzos), "los lienzos del marcado, si los hay, llevan aria-label",
            f"{len(lienzos)} lienzos")
    a.exige('lang="es"' in a.doc[:400], "el documento declara su idioma")

    # =================================================================
    a.formulas_escapadas()
    a.codificacion()
    a.coherencia(cadenas=["χ²", "σ", "√", "²", "—", "«", "»", "ó", "í", "é", "ñ", "¿", "▸", "Bogotá"],
                 ordenes=["\\(", "\\sqrt"])
    a.peso(TOPE_KB_TALLER3)
    tam = a.ruta.stat().st_size / 1024
    a.exige(tam < TOPE_KB_TALLER3 < tam + 312, "el tope queda entre el tamaño y +312 KB (arnés no ciego)",
            f"{tam:.0f} < {TOPE_KB_TALLER3:.0f} < {tam + 312:.0f}")

    if saltadas:
        print(f"\n  SALTADAS ({len(saltadas)}), declaradas y no olvidadas:")
        for s in saltadas:
            print(f"   · {s}")
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
