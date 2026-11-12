#!/usr/bin/env python3
"""
linea_base_citas.py — qué citas tiene ya la prosa, antes de marcarlas

Material de Estadística Espacial 2026-II (20929). Fase GD (2026-11-12).

Los capítulos 1–7 y el apéndice A se escribieron sin capa de fuentes: citan
«Getis y Ord (1992)» o «Anselin, 1995» como texto plano, sin `<cite>`. Este
guion barre la prosa de `precalculo/ensambla_cap*.py` y de
`ensambla_apendicea.py`, encuentra cada mención de autor y año, y la cruza con
la biblioteca del curso (`bibliografia/referencias.json`) y con los ejemplares
leídos (`ejemplares.yml`, `instantaneas.yml`):

  · catalogada-con-ejemplar  la obra está en Zotero y hay texto que leer:
                             se puede contrastar y marcar con localizador
  · catalogada-sin-ejemplar  está en Zotero pero no hay ejemplar: solo
                             lectura recomendada o cita de segunda mano
  · fuera-del-catalogo       ninguna obra de la biblioteca casa con ese
                             apellido y ese año: o falta darla de alta, o el
                             año de la prosa está mal

No juzga si la mención exige fuente (un epónimo no la exige): eso lo decide
quien redacta el plan de cada capítulo. Es el insumo de esos planes.

Uso:  python3 precalculo/linea_base_citas.py              # escribe linea_base.json
      python3 precalculo/linea_base_citas.py --comprobar  # sale con 1 si cambió
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fuentes_config import BIB, RAIZ  # noqa: E402

GUIONES = sorted((RAIZ / "precalculo").glob("ensambla_cap[0-9]*.py")) + \
    [RAIZ / "precalculo" / "ensambla_apendicea.py"]

_APELLIDO = r"(?:van den |van |von |de )?[A-ZÁÉÍÓÚÑ][^\W\d_]*(?:['’-][^\W\d_]+)*"
RE_MENCION = re.compile(
    rf"(?P<autores>{_APELLIDO}(?:(?:, | y | e | & ){_APELLIDO})*(?: et al\.)?)"
    r"(?:,? \(|, | )(?P<anio>1[6-9]\d\d|20[0-2]\d)[a-z]?\b"
)
# Palabras con mayúscula que van delante de un año sin ser autores.
NO_AUTORES = {
    "Saber", "Calendario", "Censo", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre", "EPSG", "MAGNA",
    "Bogotá", "Colombia", "Londres", "Soho", "Desde", "En", "Hasta", "Entre", "Año", "Del",
    "El", "La", "Los", "Las", "Un", "Una", "Corte", "Taller", "Parcial", "Quiz", "Semana",
    "Python", "R", "Versión", "Datum", "SIRGAS", "DANE", "MEN", "IDEAM", "ICFES", "SED",
    "WGS", "ETRS", "UTM", "ISO", "OGC", "HOLC", "GeoDa", "PySAL", "Espacial", "UNBOSQUE",
    "UnBosque", "Bosque", "EJES", "Javier", "NCGIA",
}


def ascii_min(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def apellidos(autores: str) -> list[str]:
    limpio = autores.replace(" et al.", "")
    # «de» es casi siempre la preposición («el índice de Donnelly 1978»), no la
    # partícula de un apellido; la única excepción del curso es «de Jong».
    if limpio.startswith("de ") and not limpio.startswith("de Jong"):
        limpio = limpio[3:]
    partes = re.split(r", | y | e | & ", limpio)
    return [p.strip() for p in partes if p.strip()]


def carga_biblioteca() -> tuple[list[dict], set[str]]:
    ruta = BIB / "referencias.json"
    referencias = json.loads(ruta.read_text("utf-8")) if ruta.exists() else []
    con_ejemplar: set[str] = set()
    for nombre in ("ejemplares.yml", "instantaneas.yml"):
        r = BIB / nombre
        if r.exists():
            con_ejemplar |= set((yaml.safe_load(r.read_text("utf-8")) or {}).keys())
    return referencias, con_ejemplar


def casa(ref: dict, primer_apellido: str, anio: str) -> bool:
    partes = (ref.get("issued") or {}).get("date-parts") or [[None]]
    if not partes[0] or str(partes[0][0]) != anio:
        return False
    familias = [ascii_min(a.get("family") or a.get("literal") or "") for a in ref.get("author") or []]
    objetivo = ascii_min(primer_apellido.split()[-1])
    return bool(familias) and objetivo in familias[0].split()


def barre() -> dict:
    referencias, con_ejemplar = carga_biblioteca()
    salida: dict[str, list[dict]] = {}
    for guion in GUIONES:
        if not guion.is_file():
            continue
        menciones = []
        for n, linea in enumerate(guion.read_text("utf-8").splitlines(), start=1):
            if linea.lstrip().startswith("#"):
                continue
            for m in RE_MENCION.finditer(linea):
                lista = apellidos(m.group("autores"))
                if not lista or lista[0].split()[-1] in NO_AUTORES:
                    continue
                anio = m.group("anio")
                claves = [r["id"] for r in referencias if casa(r, lista[0], anio)]
                if not claves:
                    estado = "fuera-del-catalogo"
                elif any(c in con_ejemplar for c in claves):
                    estado = "catalogada-con-ejemplar"
                else:
                    estado = "catalogada-sin-ejemplar"
                menciones.append({
                    "linea": n, "autores": m.group("autores"), "anio": anio,
                    "claves": claves, "estado": estado,
                })
        salida[guion.name] = menciones
    return salida


def resumen(datos: dict) -> dict:
    cuenta: dict[str, dict[str, int]] = {}
    for guion, menciones in datos.items():
        c = cuenta.setdefault(guion, {})
        for m in menciones:
            c[m["estado"]] = c.get(m["estado"], 0) + 1
    return cuenta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--comprobar", action="store_true", help="no escribe; sale con 1 si cambió")
    args = ap.parse_args()
    datos = barre()
    nuevo = {"resumen": resumen(datos), "menciones": datos}
    ruta = BIB / "linea_base.json"
    texto = json.dumps(nuevo, ensure_ascii=False, indent=1) + "\n"
    for guion, c in nuevo["resumen"].items():
        print(f"{guion:28s} " + " · ".join(f"{k}: {v}" for k, v in sorted(c.items())))
    if args.comprobar:
        igual = ruta.exists() and ruta.read_text("utf-8") == texto
        print("OK     linea_base.json al día" if igual else "FALLA  linea_base.json desfasada")
        return 0 if igual else 1
    ruta.write_text(texto, "utf-8")
    print(f"OK     {sum(len(v) for v in datos.values())} menciones → bibliografia/linea_base.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
