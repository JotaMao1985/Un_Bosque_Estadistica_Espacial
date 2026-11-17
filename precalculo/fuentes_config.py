"""
fuentes_config.py — dónde vive cada pieza de la capa de fuentes de 20929

Material de Estadística Espacial 2026-II (20929). Norma común:
`Bosque 2026/Vault/Estandar/Capa de fuentes.md` (v1.1).

Una sola constante por ruta, para que ningún guion la escriba dos veces.

El CORPUS (PDF, texto por página, instantáneas web) vive FUERA del repo y
FUERA de cualquier worktree, en `Trabajo 2026/Fuentes/20929/`, igual que el
de Diseño (20920). Dos razones medidas:

  · el repo es público (GitHub Pages): un libro o su texto no puede entrar;
  · un worktree nuevo no trae lo ignorado (pasó con `datos/` y con
    `precalculo/cache/`): un corpus dentro del repo obligaría a copiarlo a
    mano en cada copia de trabajo.

La variable de entorno FUENTES_20929 lo cambia (el arnés la usa para
trabajar sobre un corpus de juguete).
"""
from __future__ import annotations

import os
import pathlib

CURSO = 20929
# ESPACIAL_RAIZ la pone el arnés del ensamblador, que copia este módulo a una
# carpeta temporal: sin ella, la raíz sería la de la copia y no habría bibliografía.
RAIZ = pathlib.Path(os.environ.get("ESPACIAL_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
BIB = RAIZ / "bibliografia"
SITIO = RAIZ / "Htmls_Espacial"

RUTA_COLECCION = ["Docencia", "20929 Estadística Espacial"]
API_ZOTERO = "http://localhost:23119/api/users/0"
ALMACEN_ZOTERO = pathlib.Path.home() / "Zotero" / "storage"

CORPUS = pathlib.Path(
    os.environ.get(
        "FUENTES_20929",
        pathlib.Path.home() / "Documents" / "Trabajo 2026" / "Fuentes" / "20929",
    )
)
