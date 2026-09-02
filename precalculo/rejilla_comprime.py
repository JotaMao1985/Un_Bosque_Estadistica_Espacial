#!/usr/bin/env python3
"""
rejilla_comprime.py — el ráster, empaquetado para viajar al navegador (T3.5)

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE, con las cifras que lo justifican (A.21.3 del plan). El
capítulo 5 es el primero que publica SUPERFICIES, y una superficie no se
simplifica: se muestrea. Sus diez rásteres pesan 602 KB en la forma que
`geo_rejilla()` escribe —el array completo, con -1 en las celdas de fuera
de la ventana— y el 60,6 % de esos bytes son la cifra -1 repetida.

Dos observaciones, las dos medidas:

  1. LA MÁSCARA ES LA MISMA PARA TODAS LAS SUPERFICIES DE UNA FAMILIA.
     Las siete del deslizador de sigma comparten ventana, rejilla y caja:
     lo único que cambia es el valor. Mandarla una vez, en RLE, cuesta
     1,0 KB en vez de siete veces su parte del array.
  2. UNA KDE ES SUAVE, así que los valores contiguos de una fila se
     parecen. Publicar la diferencia con el anterior en vez del valor
     baja los dígitos de cada número.

Juntas dejan los 602 KB en 292: el 49 %, medido y no estimado.

LO QUE SE PROBÓ Y NO SIRVE, para que no se vuelva a intentar: añadir RLE
*sobre* los deltas sale PEOR que los deltas solos —32,0 KB contra 20,6 en
una superficie de Kennedy—, porque una superficie suave casi no tiene
repeticiones y las dos listas del RLE cuestan más de lo que ahorran. Y
bajar la cuantización de 1 000 a 255 niveles ahorra solo un 10 %, porque
con deltas los valores ya son pequeños.

EL FORMATO, declarado aquí porque el decodificador de la plantilla tiene
que leerlo exactamente igual:

  zqm   las longitudes de las tiradas de la máscara, alternando
  zqm0  1 si la primera tirada es DENTRO, 0 si es fuera
  zqd   los valores de las celdas de dentro, por filas y de arriba a
        abajo, cada fila empezando por su valor absoluto y siguiendo con
        diferencias respecto a la celda anterior DE ESA MISMA FILA

Y NO ES UNA CIFRA NACIENDO FUERA DE R. El navegador no calcula nada aquí:
reconstituye un array que R ya calculó. La diferencia con el `61.7` del
capítulo 1 —el número que el ensamblador calculaba y no existía en ningún
JSON— es que aquí la ida y la vuelta se comprueban byte a byte contra el
original, y si no coinciden, el ensamblado para.
"""
from __future__ import annotations


def comprime(mapa: dict) -> dict:
    """Devuelve el mapa con `zq` sustituido por `zqm`, `zqm0` y `zqd`."""
    zq, nx, ny = mapa["zq"], mapa["nx"], mapa["ny"]
    if len(zq) != nx * ny:
        raise ValueError(f"el ráster dice {nx}x{ny} y trae {len(zq)} celdas")

    # --- la máscara, en tiradas ---------------------------------------
    zqm, dentro0 = [], zq[0] >= 0
    actual, n = dentro0, 0
    for v in zq:
        d = v >= 0
        if d == actual:
            n += 1
        else:
            zqm.append(n)
            actual, n = d, 1
    zqm.append(n)

    # --- los valores, por filas y en diferencias -----------------------
    zqd = []
    for y in range(ny):
        anterior = None
        for x in range(nx):
            v = zq[y * nx + x]
            if v < 0:
                continue
            zqd.append(v if anterior is None else v - anterior)
            anterior = v

    fuera = {k: v for k, v in mapa.items() if k != "zq"}
    fuera["zqm"] = zqm
    fuera["zqm0"] = 1 if dentro0 else 0
    fuera["zqd"] = zqd
    return fuera


def expande(mapa: dict) -> list:
    """El inverso exacto. Es el gemelo del decodificador de la plantilla:
    si los dos no hacen lo mismo, el mapa sale en blanco o mentido, así
    que esta función existe para poder comprobarlo aquí, en Python, antes
    de que el navegador lo vea."""
    nx, ny = mapa["nx"], mapa["ny"]
    zq = [0] * (nx * ny)
    i, dentro = 0, mapa["zqm0"] == 1
    for largo in mapa["zqm"]:
        for _ in range(largo):
            zq[i] = 0 if dentro else -1
            i += 1
        dentro = not dentro
    if i != nx * ny:
        raise ValueError(f"la máscara cubre {i} celdas y la rejilla tiene {nx * ny}")

    p = 0
    for y in range(ny):
        acumulado, primero = 0, True
        for x in range(nx):
            k = y * nx + x
            if zq[k] < 0:
                continue
            acumulado = mapa["zqd"][p] if primero else acumulado + mapa["zqd"][p]
            p += 1
            primero = False
            zq[k] = acumulado
    if p != len(mapa["zqd"]):
        raise ValueError(f"sobran {len(mapa['zqd']) - p} diferencias sin colocar")
    return zq


def ida_y_vuelta(mapa: dict) -> dict:
    """Comprime y comprueba EN EL ACTO que se puede deshacer.

    La comprobación viaja con la función y no con quien la llama: un
    ráster mal comprimido no revienta, se dibuja distinto —y un mapa de
    calor mentido se ve igual de plausible que uno correcto, que es el
    modo de fallo que este proyecto persigue—.
    """
    c = comprime(mapa)
    if expande(c) != list(mapa["zq"]):
        raise ValueError(f"la ida y vuelta del ráster no devuelve el original")
    return c
