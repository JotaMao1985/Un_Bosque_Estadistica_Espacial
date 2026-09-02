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
import re
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


def rotulos_de_vistas(nombres: list[str]) -> list[str]:
    """La forma CORTA de cada vista de un mapa, para el rótulo del informe.

    El nombre de una vista es texto para el estudiante —«MAGNA-SIRGAS /
    Origen Nacional (9377)» gasta 37 caracteres— y un rótulo tiene 57
    contando el prefijo. Con el nombre del mapa delante,
    `proyecciones_colombia/MAGNA-SIRGAS / Origen Nacional (9377):` mide 61
    ÉL SOLO: no hay texto que quepa detrás, así que acortar la afirmación no
    arregla nada. Lo que sobra es el nombre bonito.

    Del rótulo solo se necesita que distinga una vista de las otras del
    MISMO mapa, y para un CRS eso es su código EPSG, que además es su
    identificador canónico. Se usa cuando el nombre lo trae entre
    paréntesis. Cuando no lo trae, se recorta a 12 caracteres por frontera
    de palabra: «Equal Earth» y «Mollweide» caben enteros y «Azimutal
    equidistante (Bogotá)» queda en «Azimutal». No se usa el paréntesis en
    ese caso porque «Bogotá» no identifica una proyección.

    Y si dos vistas colapsaran en el mismo corto, se devuelven los largos:
    un rótulo ambiguo es peor que uno largo. Dos comprobaciones distintas
    con el mismo rótulo se funden en una sola al contar cobertura, que es
    EXACTAMENTE el defecto que esto viene a arreglar.
    """
    cortos = []
    for n in nombres:
        m = re.search(r"\((\d{4,5})\)\s*$", n)      # (9377), (3857)…
        if m:
            cortos.append(m.group(1))
            continue
        limpio = re.sub(r"\s*\([^()]*\)\s*$", "", n).strip()
        if len(limpio) <= 12:
            cortos.append(limpio)
        else:
            corte = limpio[:12].rsplit(" ", 1)[0] if " " in limpio[:13] else limpio[:12]
            cortos.append(corte)
    return cortos if len(set(cortos)) == len(cortos) else list(nombres)


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
        vistas = mapa.get("vistas", [])
        etqs = rotulos_de_vistas([v.get("nombre", "?") for v in vistas])
        for v, etq in zip(vistas, etqs):
            cajas.append((etq, v.get("caja"), v.get("q")))
    else:
        cajas.append(("", mapa.get("caja"), mapa.get("q")))

    for etq, caja, q in cajas:
        et = f"{nombre}{'/' + etq if etq else ''}"
        if not caja or len(caja) != 4:
            a.cierto(False, f"{et}: la caja tiene 4 números", str(caja))
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
        # EL MODO `rejilla` NO CUANTIZA NADA, Y EXIGIRLE UNA `q` ERA UN
        # HUECO DEL NÚCLEO, NO UN DESCUIDO DE QUIEN LO PUBLICA. Un ráster
        # no lleva vértices: lleva una caja en coordenadas absolutas y una
        # matriz de valores. La `q` solo sirve para llevar la caja al
        # marco en el que dibuja el motor, y el pintor la da por 4096 si
        # falta. Los diez rásteres del capítulo 1 se publican sin `q`
        # desde T1.2 y por eso NUNCA han cruzado esta función —`audita_cap1`
        # los comprueba aparte—; el capítulo 5 es el primero cuyo ráster
        # vive sobre una ventana proyectada de verdad y lo destapó.
        # A cambio de no pedir `q`, se le pide lo suyo, más abajo.
        if modo == "rejilla":
            a.cierto(q is None or q in (1024, 2048, 4096),
                     f"{et}: la q, si la trae, es válida", str(q))
        else:
            a.cierto(q in (1024, 2048, 4096),
                     f"{et}: la q es válida", f"{q} (de 1024, 2048, 4096)")

    cod = mapa.get("codificacion", "absoluta")
    # 44 caracteres de texto: con `proyecciones_colombia:` delante se iba a 67
    # y arrastraba su detalle en el informe del capítulo 2 exactamente igual
    # que los dos de más abajo. Aquí no lo cazó nadie porque el detector vive
    # en el arnés del taller y los mapas del taller tienen nombres cortos: es
    # el mismo defecto, latente. «de la geometría» sobra —esto audita un
    # geomapa— y el detalle ya imprime cuál es.
    a.cierto(cod in ("absoluta", "delta"),
             f"{nombre}: la codificación va declarada", cod)
    # TODAS LAS COORDENADAS, NO SOLO LAS DE `geom`. Hasta el capítulo 4
    # esto miraba únicamente los polígonos, y por eso una `q` mentida
    # pasaba sin más en un mapa de modo `puntos`: lo destapó el arnés de
    # inyección del capítulo 4, cuyos siete mapas son todos de ese modo.
    # Los capítulos 1 a 3 nunca lo notaron porque sus mapas llevan `geom`
    # y la comprobación sí mordía ahí. Las coordenadas de `pts`, de las
    # polilíneas de fondo y de la capa `puntos2` viven en la MISMA
    # cuantización, así que se validan igual.
    def _coords_de(parte, delta=False):
        if delta:
            xs, ys, ax, ay = [], [], 0, 0
            for i in range(0, len(parte), 2):
                ax = parte[i] if i == 0 else ax + parte[i]
                ay = parte[i + 1] if i == 0 else ay + parte[i + 1]
                xs.append(ax); ys.append(ay)
            return xs + ys
        return list(parte)

    partes_xy = []
    for rasgo in mapa.get("geom") or []:
        for parte in rasgo:
            partes_xy.append(_coords_de(parte, cod == "delta"))
    for campo in ("pts", "puntos2"):
        if mapa.get(campo):
            partes_xy.append(list(mapa[campo]))
    for linea in mapa.get("lineas") or []:
        partes_xy.append(list(linea))

    if partes_xy:
        q = mapa.get("q") or 4096
        todos = [v for parte in partes_xy for v in parte]
        lo, hi = min(todos), max(todos)
        # LOS DOS RÓTULOS DE AQUÍ ABAJO TIENEN PRESUPUESTO: 57 CARACTERES
        # CONTANDO `{nombre}: `. `Auditoria.cierto()` rellena el rótulo hasta
        # 58 antes del detalle, así que uno de 58 o más se queda sin relleno,
        # queda pegado a su detalle por un solo espacio, y quien lee el
        # informe con una expresión regular —`prueba_auditor_taller1.py`— no
        # puede separarlos: el mismo control cuenta como un tipo distinto por
        # cada valor del detalle, y la cobertura sale subestimada SIN QUE NADA
        # FALLE. El rótulo largo no rompe la comprobación; rompe el recuento
        # de qué comprobaciones se han visto fallar.
        #
        # Va por la TERCERA vez. Se acortaron cinco rótulos, volvió a pasar en
        # uno escrito después, y volvió otra vez aquí: estas dos líneas nacieron
        # cortas y se alargaron al ampliarlas a todas las coordenadas para el
        # capítulo 4 —donde `proyecciones_colombia:` gasta 23 de los 57—.
        # Por eso el texto va corto y CON HOLGURA, y la explicación vive en
        # este comentario y en el detalle, que no paga presupuesto.
        a.cierto(-1 <= lo and hi <= q + 1,
                 f"{nombre}: las coordenadas caben en la q",
                 f"[{lo}, {hi}] con q = {q}")
        a.cierto(hi > q * 0.5,
                 f"{nombre}: y la q no está inflada",
                 f"máximo {hi} de {q}")

    # EL CONTRATO PROPIO DEL RÁSTER, que es lo que sustituye a la `q`.
    # Sin esto, cambiar `nx` por su cuenta, perder celdas por el camino o
    # publicar un valor por encima de la cuantización declarada pasaba sin
    # que nada lo mirara: el modo `rejilla` llevaba desde T0.3 en la lista
    # de los cinco y sin una sola comprobación propia en el núcleo.
    if modo == "rejilla":
        nx, ny = mapa.get("nx"), mapa.get("ny")
        zq, zqmax = mapa.get("zq"), mapa.get("zqmax")
        a.cierto(isinstance(nx, int) and isinstance(ny, int) and nx > 0 and ny > 0,
                 f"{nombre}: la rejilla declara sus dos lados", f"{nx} x {ny}")
        a.cierto(isinstance(zq, list) and isinstance(zqmax, (int, float)) and zqmax > 0,
                 f"{nombre}: el ráster trae valores y cuantización", str(zqmax))
        # COMPROBAR UN VALOR Y USARLO NO ES LO MISMO, y aquí se separaron
        # dos líneas: se validaba que `zqmax` fuera positivo y a
        # continuación se usaba sin condicionar, así que un `zqmax` nulo
        # MATABA al auditor en vez de que informara. Lo destapó el arnés
        # del capítulo 5 el mismo día que `revento()` subió a distinguir
        # «informó» de «murió»: antes de eso, ese reventón se habría
        # contado como captura.
        if (isinstance(zq, list) and zq and isinstance(nx, int) and isinstance(ny, int)
                and isinstance(zqmax, (int, float)) and zqmax > 0):
            a.igual(len(zq), nx * ny, f"{nombre}: hay una celda por posición")
            lo_z, hi_z = min(zq), max(zq)
            # -1 es «celda sin dato», el convenio que el pintor lee para
            # saltarse lo que cae fuera de la ventana. Cualquier otro
            # negativo es un valor corrupto disfrazado de máscara.
            a.cierto(lo_z >= -1, f"{nombre}: ningún valor por debajo de -1", str(lo_z))
            a.cierto(hi_z <= zqmax, f"{nombre}: nada se sale de la cuantización",
                     f"{hi_z} de {zqmax}")

    kb = len(json.dumps(mapa, ensure_ascii=False).encode("utf-8")) / 1024
    a.cierto(kb <= presupuesto_kb, f"{nombre}: cabe en el presupuesto",
             f"{kb:.1f} KB de {presupuesto_kb:.0f}")
    return kb
