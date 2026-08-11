#!/usr/bin/env python3
"""
audita_base.py — el núcleo compartido de los auditores de precálculo (T2.1d)

Material de Estadística Espacial 2026-II (20929).

POR QUÉ ESTO EXISTE, Y POR QUÉ SE EXTRAE AHORA Y NO ANTES.

`audita_texto_base.py` ya había aprendido esta lección en T0.5: en Diseño
de Experimentos cada auditor de prosa llevaba su propio núcleo cableado, y
un fallo —retirar las fórmulas de KaTeX antes de extraer los números—
sobrevivió en CINCO auditores a la vez, todos informando «limpio».

Los auditores de PRECÁLCULO estaban a punto de repetirlo: `audita_cap1.py`
lleva su clase `Auditoria` dentro, y el capítulo 2 iba a llevar una copia.
Con dos copias todavía se puede arreglar; con diez, no. Así que el
contador de comprobaciones, el registro de fallos, el de saltadas y el
formato del informe viven aquí, y cada capítulo aporta solo lo que sabe
comprobar.

Lo que NO sube aquí: nada específico de un capítulo. Este archivo no
conoce ninguna cifra ni ninguna fuente.

Las cuatro formas de comprobar, y son distintas a propósito:

  igual()   tolerancia ABSOLUTA. Para proporciones, correlaciones y
            cualquier cosa de orden 1.
  cerca()   tolerancia RELATIVA. Para áreas en m², distancias en m y
            bytes, donde 1e-6 absoluto no significa nada.
  cierto()  para lo que no es un número: banderas, cadenas, conteos.
  salta()   una comprobación que NO se hace, DICHA EN VOZ ALTA. Callarla
            la convertiría en una comprobación imaginaria, que sobre el
            informe se lee igual que una que sí corrió.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys


class Auditoria:
    def __init__(self, titulo_cierre: str = "Precálculo verificado") -> None:
        self.n = 0
        self.fallos: list[str] = []
        self.saltadas: list[str] = []
        self.titulo_cierre = titulo_cierre

    def igual(self, calculado, publicado, que: str, tol: float = 1e-6) -> bool:
        """Contrasta un número recalculado aquí contra el que se publicó."""
        self.n += 1
        try:
            a, b = float(calculado), float(publicado)
        except (TypeError, ValueError):
            self.fallos.append(f"{que}: no es un número ({calculado!r} / {publicado!r})")
            print(f"  MAL  {que:<58} no es un número")
            return False
        if a != a or b != b:            # NaN: nunca es igual a nada, ni a sí mismo
            self.fallos.append(f"{que}: hay un NaN ({a} / {b})")
            print(f"  MAL  {que:<58} NaN")
            return False
        d = abs(a - b)
        ok = d <= tol
        print(f"  {'OK ' if ok else 'MAL'}  {que:<58} {a:>16.8f} {b:>16.8f}")
        if not ok:
            self.fallos.append(f"{que}: {a:.8f} frente a {b:.8f} (dif {d:.3e})")
        return ok

    def cerca(self, calculado, publicado, que: str, rel: float = 1e-6) -> bool:
        """Tolerancia RELATIVA, para magnitudes grandes (áreas en m², bytes)."""
        base = max(abs(float(publicado)), 1e-12)
        return self.igual(calculado, publicado, que, tol=rel * base)

    def cierto(self, cond, que: str, detalle: str = "") -> bool:
        self.n += 1
        ok = bool(cond)
        print(f"  {'OK ' if ok else 'MAL'}  {que:<58} {detalle}")
        if not ok:
            self.fallos.append(f"{que} {detalle}".strip())
        return ok

    def salta(self, que: str, motivo: str) -> None:
        self.saltadas.append(f"{que} — {motivo}")
        print(f"  ···  {que:<58} SALTADA: {motivo}")

    def titulo(self, t: str) -> None:
        print(f"\n=== {t} " + "=" * max(0, 56 - len(t)))

    def cierre(self) -> int:
        print("\n=== Cierre " + "=" * 52)
        print(f"\n  {self.n} comprobaciones · {len(self.fallos)} fallos"
              f" · {len(self.saltadas)} saltadas")
        if self.saltadas:
            print("\n  SALTADAS (declaradas, no olvidadas):")
            for s in self.saltadas:
                print(f"   · {s}")
        if self.fallos:
            print("\n  FALLOS:")
            for f in self.fallos:
                print(f"   - {f}")
            return 1
        print(f"\n  {self.titulo_cierre}.\n")
        return 0


def carga(var: str, nombre: str, salidas: pathlib.Path):
    """El JSON publicado, o la copia con defectos que apunte `var`.

    La variable de entorno es lo que permite que el arnés de inyección
    audite una copia envenenada sin tocar jamás los archivos publicados.
    """
    p = pathlib.Path(os.environ.get(var) or (salidas / nombre))
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return json.loads(p.read_text(encoding="utf-8")), p


def decimales(o, ruta=""):
    """Genera (ruta, nº de decimales) de cada flotante del objeto.

    Sirve a la regla de T0.5: el JSON se guarda con HOLGURA (10 decimales)
    por debajo de lo que la prosa publica (5), o hay doble redondeo entre
    el texto y el bloque de código del propio capítulo.
    """
    if isinstance(o, dict):
        for k, v in o.items():
            yield from decimales(v, f"{ruta}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from decimales(v, f"[{i}]" if not ruta else f"{ruta}[{i}]")
    elif isinstance(o, float):
        t = repr(o)
        if "." in t and "e" not in t and "E" not in t:
            yield ruta, len(t.split(".")[1])


def sin_nan(o, ruta=""):
    """Genera la ruta de cada NaN o infinito escondido en el objeto."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from sin_nan(v, f"{ruta}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from sin_nan(v, f"{ruta}[{i}]")
    elif isinstance(o, float):
        if o != o or o in (float("inf"), float("-inf")):
            yield ruta


def audita_geomapa(a: Auditoria, mapa: dict, nombre: str, presupuesto_kb: float = 120.0):
    """Las comprobaciones que valen para CUALQUIER `.geomapa`.

    Están aquí y no en cada capítulo porque son propiedades del
    componente, no del contenido: la caja tiene que estar ordenada, la
    cuantización tiene que ser la declarada, y —el criterio duro de
    T0.3— la escala en x tiene que ser idéntica a la de y, porque un
    mapa con escalas distintas es un mapa mal dibujado.
    """
    modo = mapa.get("modo")
    a.cierto(modo in ("poligonos", "puntos", "grafo", "rejilla", "proyeccion"),
             f"{nombre}: el modo es uno de los cinco", str(modo))

    cajas = []
    if modo == "proyeccion":
        for v in mapa.get("vistas", []):
            cajas.append((v.get("nombre", "?"), v.get("caja"), v.get("q")))
    else:
        cajas.append(("", mapa.get("caja"), mapa.get("q")))

    for etq, caja, q in cajas:
        et = f"{nombre}{'/' + etq if etq else ''}"
        if not caja or len(caja) != 4:
            a.cierto(False, f"{et}: la caja tiene cuatro números", str(caja))
            continue
        a.cierto(caja[0] < caja[2] and caja[1] < caja[3],
                 f"{et}: la caja está ordenada",
                 f"x [{caja[0]:.1f}, {caja[2]:.1f}] y [{caja[1]:.1f}, {caja[3]:.1f}]")
        # La cuantización dejó de estar cableada a 4096 en T2.4: un mapa
        # de 1 122 municipios va a 1024 y declara su q. Eso NO afloja la
        # comprobación —aflojarla sería aceptar cualquier número— sino
        # que la sustituye por una más fuerte: la q tiene que ser una de
        # las declaradas Y las coordenadas tienen que caer de verdad
        # dentro de ella. Una q mentida se ve enseguida: los vértices se
        # salen del rango o no llegan ni a la mitad.
        a.cierto(q in (1024, 2048, 4096),
                 f"{et}: la cuantización es una de las del componente", str(q))

    cod = mapa.get("codificacion", "absoluta")
    a.cierto(cod in ("absoluta", "delta"),
             f"{nombre}: la codificación de la geometría va declarada", cod)
    if mapa.get("geom"):
        q = mapa.get("q") or 4096
        lo = hi = None
        for rasgo in mapa["geom"]:
            for parte in rasgo:
                if cod == "delta":
                    xs, ys = [], []
                    ax = ay = 0
                    for i in range(0, len(parte), 2):
                        ax = parte[i] if i == 0 else ax + parte[i]
                        ay = parte[i + 1] if i == 0 else ay + parte[i + 1]
                        xs.append(ax); ys.append(ay)
                else:
                    xs, ys = parte[0::2], parte[1::2]
                for v in xs + ys:
                    lo = v if lo is None else min(lo, v)
                    hi = v if hi is None else max(hi, v)
        a.cierto(lo is not None and -1 <= lo and hi <= q + 1,
                 f"{nombre}: los vértices caen dentro de la cuantización declarada",
                 f"[{lo}, {hi}] con q = {q}")
        a.cierto(hi is not None and hi > q * 0.5,
                 f"{nombre}: y la ocupan de verdad (la q no está inflada)",
                 f"máximo {hi} de {q}")

    kb = len(json.dumps(mapa, ensure_ascii=False).encode("utf-8")) / 1024
    a.cierto(kb <= presupuesto_kb, f"{nombre}: cabe en el presupuesto",
             f"{kb:.1f} KB de {presupuesto_kb:.0f}")
    return kb
