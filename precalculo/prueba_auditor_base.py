#!/usr/bin/env python3
"""
prueba_auditor_base.py — la maquinaria común de los arneses de inyección (T2.1d)

Material de Estadística Espacial 2026-II (20929).

Se extrae junto con `audita_base.py` y por el mismo motivo: la maquinaria
—copiar los JSON a un temporal, mutar la copia, invocar al auditor con las
variables de entorno apuntadas ahí, contar cazados y contar cuántas
comprobaciones distintas se han visto fallar— es idéntica en todos los
capítulos. Lo único que cambia es la LISTA DE DEFECTOS, que sí es del
capítulo y se queda en su archivo.

LAS DOS REGLAS DEL ARNÉS, las dos aprendidas a golpes y las dos aquí
dentro para que ningún capítulo pueda saltárselas:

  1. **Cada tanda empieza y acaba con un CONTROL sin inyectar nada.** Si
     el auditor no sale limpio sobre el original, cualquier «acierto»
     posterior es falso. Es lo que cazó, en T1.2, que el fixture de T0.5
     había dejado de funcionar y sus 36 inyecciones no probaban nada.
  2. **«49 de 49» no basta.** Se cuenta también cuántas comprobaciones
     DISTINTAS se han visto fallar alguna vez. Una comprobación que nunca
     ha fallado puede estar bien escrita o puede ser incapaz de fallar, y
     desde fuera se ven igual.

Y una tercera, que es del arnés y no del auditor: **una mutación que no
cambia el archivo se declara error del arnés**, no «defecto no detectado».
Registrar un fallo del auditor cuando el culpable es la inyección
envenena el informe en la dirección contraria.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


def corre(py, auditor, archivos, rutas):
    entorno = dict(os.environ)
    for clave, ruta in rutas.items():
        entorno[archivos[clave][0]] = str(ruta)
    res = subprocess.run([py, str(auditor)], capture_output=True, text=True,
                         cwd=str(auditor.resolve().parent.parent), env=entorno)
    return res.returncode, res.stdout + res.stderr


def resumen(salida: str) -> str:
    m = re.search(r"(\d+) comprobaciones · (\d+) fallos", salida)
    return m.group(0) if m else "(sin resumen)"


def nombres(salida: str, estado: str) -> set[str]:
    fuera = set()
    for linea in salida.splitlines():
        m = re.match(r"\s{2}" + re.escape(estado) + r"\s{2,}(\S.*?)\s{2,}", linea + "  ")
        if m:
            fuera.add(m.group(1).strip())
    return fuera


# El ancho al que `Auditoria` rellena el rótulo antes del detalle. No es un
# número de estilo: es el que decide si `nombres()` puede separar los dos.
ANCHO_ROTULO = 58


def avisa_rotulos_largos(todas: set[str]) -> int:
    """El detector que convierte un defecto recurrente en uno visible.

    `Auditoria.cierto()` escribe `f"{que:<58} {detalle}"`. Un rótulo de 58
    o más se queda sin relleno, así que entre él y su detalle no queda más
    que UN espacio — y `nombres()` corta por dos—. El rótulo extraído se
    lleva el detalle pegado, el detalle cambia entre la pasada limpia y la
    rota, y entonces el rótulo que sale MAL no es el mismo que salió OK:
    **la comprobación no se cuenta como cubierta aunque haya fallado**.

    Nada falla por esto. Lo que se corrompe es el recuento de cobertura, y
    en silencio, que es la clase de defecto que este arnés existe para no
    tener. Por eso AVISA en vez de acortar: acortar arregla la instancia y
    ya ha vuelto tres veces —cinco rótulos en T0.5, uno escrito después en
    C5b, y en 2026-08-24 los dos de `audita_geomapa()` al ampliarla para el
    capítulo 4, más 69 en el capítulo 2, 83 en el 1 y 12 en el 3—.

    Vive aquí, y no en cada arnés, por lo mismo que el resto de la
    maquinaria: nació en `prueba_auditor_taller1.py`, que es el único que
    contaba TIPOS y por eso el único que lo notó. Los capítulos tenían el
    mismo agujero y ningún ojo puesto encima.

    No es un fallo: devuelve cuántos hay y no toca el código de salida. Un
    capítulo con rótulos largos sigue estando bien auditado; lo que no está
    es bien MEDIDO, y eso se dice, no se castiga.
    """
    largos = sorted(x for x in todas if len(x) >= ANCHO_ROTULO)
    if largos:
        print(f"\n  ---  {len(largos)} rótulo(s) de {ANCHO_ROTULO} caracteres o más: "
              f"arrastran su detalle y\n       falsean el recuento de cobertura. "
              f"Acórtalos en el auditor:")
        for x in largos[:20]:
            print(f"         ({len(x)}) {x[:70]}")
        if len(largos) > 20:
            print(f"         · … y {len(largos) - 20} más")
    return len(largos)


def arnes(titulo: str, py: str, auditor: pathlib.Path, salidas: pathlib.Path,
          archivos: dict, lista, pista_generadores: str) -> int:
    """Ejecuta la tanda entera. `lista` es [(nombre, clave, tipo, acción)]."""
    for _, nombre in archivos.values():
        if not (salidas / nombre).exists():
            print(f"PARADO: falta {salidas / nombre}. Ejecuta antes {pista_generadores}")
            return 1

    originales = {c: (salidas / n).read_bytes() for c, (_, n) in archivos.items()}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arnes_"))
    limpias = {}
    for clave, (_, nombre) in archivos.items():
        limpias[clave] = tmp / nombre
        shutil.copy(salidas / nombre, limpias[clave])

    print("=" * 66)
    print(f"  {titulo}")
    print("=" * 66)

    # --- CONTROL DE ENTRADA ------------------------------------------
    codigo, salida = corre(py, auditor, archivos, limpias)
    print(f"\n  {'OK ' if codigo == 0 else 'MAL'}  control de entrada · sin inyectar nada")
    print(f"        {resumen(salida)}")
    if codigo != 0:
        print("\n  PARADO: el control falla, así que el arnés no prueba nada.")
        for linea in salida.strip().splitlines():
            if linea.strip().startswith("- "):
                print(f"        {linea.strip()}")
        shutil.rmtree(tmp, ignore_errors=True)
        return 1

    todas = nombres(salida, "OK ")
    avisa_rotulos_largos(todas)
    vistas_fallar: set[str] = set()
    cazados = 0
    fallos_del_arnes = 0
    print(f"\n  {len(lista)} defectos que inyectar\n" + "-" * 66)

    for nombre_d, clave, tipo, accion in lista:
        rutas = dict(limpias)
        rota = tmp / f"roto_{archivos[clave][1]}"
        if tipo == "obj":
            obj = json.loads(limpias[clave].read_text(encoding="utf-8"))
            antes = json.dumps(obj, ensure_ascii=False, sort_keys=True)
            try:
                accion(obj)
            except Exception as e:                      # noqa: BLE001
                print(f"  MAL  {nombre_d}\n        la mutación reventó: {e}")
                fallos_del_arnes += 1
                continue
            despues = json.dumps(obj, ensure_ascii=False, sort_keys=True)
            if antes == despues:
                print(f"  MAL  {nombre_d}\n        la mutación no cambió el archivo")
                fallos_del_arnes += 1
                continue
            rota.write_text(json.dumps(obj, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        else:
            busca, pone = accion
            txt = limpias[clave].read_text(encoding="utf-8")
            if txt.count(busca) < 1:
                print(f"  MAL  {nombre_d}\n"
                      f"        el texto a sustituir no aparece: {busca[:60]!r}")
                fallos_del_arnes += 1
                continue
            rota.write_text(txt.replace(busca, pone, 1), encoding="utf-8")
        rutas[clave] = rota

        codigo, salida = corre(py, auditor, archivos, rutas)
        ok = codigo != 0
        cazados += ok
        print(f"  {'OK ' if ok else 'MAL'}  {nombre_d}")
        print(f"        {resumen(salida)}")
        if ok:
            vistas_fallar |= nombres(salida, "MAL")
        else:
            print("        NO DETECTADO — el auditor dio el archivo por bueno")

    # --- CONTROL DE SALIDA -------------------------------------------
    codigo, salida = corre(py, auditor, archivos, limpias)
    print("\n" + "-" * 66)
    print(f"  {'OK ' if codigo == 0 else 'MAL'}  control de salida · el arnés no dejó nada tocado")
    intactos = all((salidas / n).read_bytes() == originales[c]
                   for c, (_, n) in archivos.items())
    print(f"  {'OK ' if intactos else 'MAL'}  los archivos publicados siguen byte a byte igual")

    shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 66)
    print(f"  {cazados} de {len(lista)} defectos cazados")
    if fallos_del_arnes:
        print(f"  {fallos_del_arnes} inyecciones fallaron POR CULPA DEL ARNÉS, no del auditor")
    print(f"  {len(vistas_fallar)} de {len(todas)} comprobaciones se han visto fallar")
    restantes = sorted(todas - vistas_fallar)
    if restantes:
        print(f"\n  Sin ver fallar ({len(restantes)}). La mayoría son otras "
              f"instancias de\n  mecanismos ya demostrados —otro dato, otra "
              f"proyección, otro par—, pero\n  la lista se imprime para que "
              f"nadie tenga que fiarse de eso:")
        for r in restantes[:20]:
            print(f"    · {r}")
        if len(restantes) > 20:
            print(f"    · … y {len(restantes) - 20} más")
    print("=" * 66)

    malo = (cazados != len(lista)) or codigo != 0 or not intactos or fallos_del_arnes
    return 1 if malo else 0
