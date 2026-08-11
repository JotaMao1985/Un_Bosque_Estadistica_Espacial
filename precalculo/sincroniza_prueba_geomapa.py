#!/usr/bin/env python3
"""
sincroniza_prueba_geomapa.py — mantiene el banco de pruebas del `.geomapa`
al día con la plantilla y con el precálculo (T2.1a)

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE.

El §9 del plan tiene una regla fija: un componente nuevo se retropropaga
**en la misma sesión** a la plantilla y a `Htmls_Espacial/prueba-geomapa.html`.
El problema es que `prueba-geomapa.html` se ensambló A MANO en T0.3 y no
tenía guion, así que la regla dependía de que alguien se acordara de
copiar el motor y de volver a pegar el JSON. Una regla que depende de la
memoria se incumple: en T1.2 el motor del banco de pruebas y el de la
plantilla ya habían empezado a separarse, y un banco de pruebas que
prueba una versión vieja del componente no prueba nada.

Esto lo hace mecánico. Dos sustituciones, las dos con anclas exactas:

  1. EL MOTOR — desde `const GEOMAPAS = {};` hasta el final de
     `destruirGeomapas()`. Se copia literalmente de la plantilla, que es
     la fuente de verdad del componente.
  2. LOS DATOS — la línea `const DEMO = ...;`, que se rehace desde
     `precalculo/demo_geomapa.json`.

Las guardas son las de `ensambla_cap1.py`, y por el mismo motivo: cada
ancla tiene que aparecer EXACTAMENTE UNA VEZ, y la región sustituida
declara tope máximo Y MÍNIMO. El mínimo está porque en T1.2 un ancla de
cierre casó demasiado pronto, dejó media sección viva, y el archivo salió
bien formado y el informe en verde.

Uso:  python3 precalculo/sincroniza_prueba_geomapa.py
      (desde la carpeta `Estadistica espacial/`)
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import json
import re
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
BANCO = RAIZ / "Htmls_Espacial" / "prueba-geomapa.html"
DEMO_JSON = RAIZ / "precalculo" / "demo_geomapa.json"

ABRE = "    const GEOMAPAS = {};"
CIERRA = (
    "    function destruirGeomapas() {\n"
    "      geomapasVivos.forEach(g => { try { g.ro.disconnect(); } catch (e) { /* ya desconectado */ } });\n"
    "      geomapasVivos = [];\n"
    "    }\n"
)


def extrae(texto: str, abre: str, cierra: str, que: str) -> str:
    """El bloque [abre, cierra] con las dos anclas dentro, exigiendo unicidad."""
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de {que} aparece {texto.count(abre)} veces")
    if texto.count(cierra) != 1:
        sys.exit(f"PARADO: el ancla de cierre de {que} aparece {texto.count(cierra)} veces")
    i = texto.index(abre)
    j = texto.index(cierra, i)
    if j < i:
        sys.exit(f"PARADO: el cierre de {que} va antes que la apertura")
    return texto[i:j + len(cierra)]


def main() -> int:
    if not BANCO.exists():
        sys.exit(f"PARADO: no está {BANCO}")
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    banco = BANCO.read_text(encoding="utf-8")

    motor_bueno = extrae(plantilla, ABRE, CIERRA, "el motor de la plantilla")
    motor_viejo = extrae(banco, ABRE, CIERRA, "el motor del banco")

    n_bueno = motor_bueno.count("\n")
    n_viejo = motor_viejo.count("\n")
    # Tope máximo Y mínimo, igual que en ensambla_cap1.py. Un motor que
    # de pronto mide la mitad o el doble no es una mejora: es un ancla
    # que casó donde no debía.
    if not (0.5 * n_viejo <= n_bueno <= 2.0 * n_viejo):
        sys.exit(f"PARADO: el motor de la plantilla mide {n_bueno} líneas y el del banco "
                 f"{n_viejo}; fuera del margen [0,5x, 2x]. Revisa las anclas antes de pisar nada")

    cambio_motor = motor_bueno != motor_viejo
    banco = banco.replace(motor_viejo, motor_bueno)

    # --- Los datos ------------------------------------------------------
    lineas = banco.splitlines(keepends=True)
    idx = [i for i, l in enumerate(lineas) if l.startswith("    const DEMO = ")]
    if len(idx) != 1:
        sys.exit(f"PARADO: {len(idx)} líneas `const DEMO = `, se esperaba 1")
    demo = json.loads(DEMO_JSON.read_text(encoding="utf-8"))
    nueva = "    const DEMO = " + json.dumps(demo, ensure_ascii=False,
                                             separators=(", ", ": ")) + ";\n"
    cambio_datos = lineas[idx[0]] != nueva
    lineas[idx[0]] = nueva
    banco = "".join(lineas)

    BANCO.write_text(banco, encoding="utf-8")

    # --- Guardas de salida ----------------------------------------------
    # Que el guion escriba no significa que haya escrito bien.
    problemas = []
    if banco.count(ABRE) != 1:
        problemas.append("el motor quedó duplicado o desaparecido")
    if banco.count("    const DEMO = ") != 1:
        problemas.append("hay más de un `const DEMO`")
    usados = set(re.findall(r'data-geomapa="([^"]+)"', banco))
    # El registro se busca con expresión regular y no partiendo cadenas:
    # el banco alinea los `=` en columna (`GEOMAPAS['puntos']    = {`), y
    # una comprobación que buscara el literal `"] ="` daba tres mapas por
    # no registrados sobre un archivo correcto. Un auditor que denuncia lo
    # que está bien se acaba desactivando — es la lección de A.3.
    codigo = "\n".join(l for l in banco.splitlines() if not l.lstrip().startswith("//"))
    registrados = set(re.findall(r"GEOMAPAS\['([^']+)'\]\s*=", codigo))
    huerfanos = usados - registrados
    if huerfanos:
        problemas.append(f"mapas usados y no registrados: {sorted(huerfanos)}")

    print(f"\n=== sincroniza_prueba_geomapa.py ===")
    print(f"  motor: {'ACTUALIZADO' if cambio_motor else 'ya estaba al día'} "
          f"({n_bueno} líneas)")
    print(f"  datos: {'ACTUALIZADOS' if cambio_datos else 'ya estaban al día'} "
          f"({DEMO_JSON.stat().st_size / 1024:.1f} KB)")
    print(f"  {BANCO.relative_to(RAIZ)}  {len(banco) / 1024:.0f} KB · "
          f"{len(usados)} mapas usados, {len(registrados)} registrados")
    if problemas:
        for p in problemas:
            print(f"  FALLA: {p}")
        return 1
    print("  OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
