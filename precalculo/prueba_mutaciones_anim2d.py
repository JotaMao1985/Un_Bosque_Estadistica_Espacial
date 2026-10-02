#!/usr/bin/env python3
"""
prueba_mutaciones_anim2d.py — le rompe el motor 2D a su prueba y exige que lo cace

Material de Estadística Espacial 2026-II (20929). Capítulo 6, módulo 10.

POR QUÉ EXISTE. Una prueba que da «todo en verde» la primera vez no ha demostrado nada:
puede comprobar bien o puede comprobar cosas incapaces de fallar. `prueba_rezago2d.py`
compara la aritmética de `rezago2d.js` con R y prueba la máquina de `anim2d.js` sin DOM;
aquí se le inyecta, uno a uno, un defecto de los que este motor puede tener de verdad, en
una COPIA del archivo (la prueba lee la copia por `REZAGO2D_MOTOR` y `ANIM2D_NUCLEO`), y se
exige que la prueba falle. Un defecto que pase es un hueco de la prueba, no del motor.

LAS FAMILIAS, y cada una imita algo que este código podría sufrir:

   · de la aritmética: arista en base 0, desviación con n en vez de n − 1, media dividida
     por n en vez de por el grado, una capa de menos, el límite como media simple
   · LA QUE EL CAPÍTULO ACABA DE CORREGIR: la pendiente de Wy sobre y escrita como la
     correlación (cov / (sd·sd) en vez de cov / var)
   · de la vecindad: reina servida como torre
   · de la geometría: el eje y del clic sin invertir, un trazado de rayos que da por dentro
     cualquier punto con un cruce, la caja del dato contra el encuadre equivocado
   · del estado: k sin acotar, el teclado que no da la vuelta, la escala de color por capa, la lupa que no
     acerca, que deja fuera a los vecinos o cuyo clic ignora la caja que se ve
   · de la máquina: `poner` que acepta NaN o claves que no existen, una transición que no
     llega, un gesto que no interrumpe el guion, un guion que no se detiene, `reproducir`
     que no vuelve a empezar, una API inerte a la que le falta un método, las transiciones
     que ignoran prefers-reduced-motion, un paso cuyo estado-función no se evalúa
   · del gesto y de lo que la revisión en Chrome encontró (2026-10-02): el toque que elige al
     bajar el dedo, la salida del lienzo que para el guion, el toque desplazado o cancelado que
     elige igual; el deslizador que no cambia el paso, «casi un solo color» con cualquier k,
     la cuenta con «=», W² que da por seguros a todos los vecinos, k que no llega a 66
   · de la auditoría de las cinco animaciones (2026-10-02): el guion que no da tiempo a leer

UNA INYECCIÓN NO PUEDE SER UN EQUIVALENTE, y la primera versión de esta lista tenía uno: mirar el
rayo hacia el otro lado (`qx > …` en vez de `qx < …`) da el MISMO resultado, porque una recta que
cruza un polígono cerrado lo corta un número par de veces y los cruces a un lado y a otro tienen la
misma paridad. Se quitó. Tampoco valen el barrio de partida con otro umbral de vecinos ni `reinicia`
sin su `ir(1)`: el motor las absorbe.

    python3 precalculo/prueba_mutaciones_anim2d.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRE = RAIZ / "precalculo"
REZAGO = PRE / "anim2d" / "rezago2d.js"
NUCLEO = PRE / "anim2d" / "anim2d.js"
PRUEBA = PRE / "prueba_rezago2d.py"

# (nombre, archivo, busca, pone). `busca` tiene que aparecer UNA vez: si el motor cambia y deja de
# aparecer, el arnés para (y avisa) en vez de callar.
MUTACIONES = [
    # --- la aritmética ---
    ("las aristas se leen en base 0 (sin restar 1)", REZAGO,
     "const a = aristas[i] - 1, b = aristas[i + 1] - 1;", "const a = aristas[i], b = aristas[i + 1];"),
    ("la desviación divide por n en vez de n − 1", REZAGO,
     "return Math.sqrt(s / (v.length - 1));", "return Math.sqrt(s / v.length);"),
    ("la covarianza divide por n y la desviación por n − 1 (la correlación se descuadra)", REZAGO,
     "return s / (a.length - 1);", "return s / a.length;"),
    ("el rezago divide por n en vez de por el grado", REZAGO,
     "return s / nb.length;", "return s / vec.length;"),
    ("las capas se desplazan una (k − 1 donde va k)", REZAGO,
     "out.push(rezago(vec, out[k - 1]));", "out.push(rezago(vec, out[Math.max(0, k - 2)]));"),
    ("el límite es la media simple y no la ponderada por el grado", REZAGO,
     "num += vec[i].length * y[i]; den += vec[i].length;", "num += y[i]; den += 1;"),
    ("la pendiente se calcula como la correlación (el error que se corrigió en el capítulo)", REZAGO,
     "pendiente: cov(y, v) / cov(y, y)", "pendiente: cov(y, v) / (sd(y) * sd(v))"),
    # --- la vecindad ---
    ("la reina se sirve como torre y la torre como reina", REZAGO,
     "const v = mapa.variantes[nombre];", "const v = mapa.variantes[nombre === 'reina' ? 'torre' : 'reina'];"),
    # --- la geometría ---
    ("el clic no invierte el eje y", REZAGO,
     "qy: py => cq.y1 - (py - oy) / s", "qy: py => cq.y0 + (py - oy) / s"),
    ("el trazado de rayos da por dentro cualquier punto con un cruce", REZAGO,
     "(xj - xi) * (qy - yi) / (yj - yi) + xi) ad = !ad;", "(xj - xi) * (qy - yi) / (yj - yi) + xi) ad = true;"),
    ("la caja del dato se encuadra con el lado corto", REZAGO,
     "const r = Math.max(rx, ry);", "const r = Math.min(rx, ry);"),
    # --- el estado y lo que ve la persona ---
    ("k no se acota", REZAGO,
     "out.k = Math.min(K_MAX, Math.max(0, Math.round(out.k)));", "out.k = Math.round(out.k);"),
    ("el deslizador vuelve a quedarse en k = 60, antes de las 66 aplicaciones que cita la prosa", REZAGO,
     "const K_MAX = 70;", "const K_MAX = 60;"),
    ("el deslizador no cambia el paso (la leyenda de y se queda encima de W³⁰y)", REZAGO,
     "if ('k' in out && !('paso' in out)) out.paso = pasoDeK(out.k);", ""),
    ("el paso 4 dice «casi un solo color» con cualquier k", REZAGO,
     "const casiUno = E => de(E.vecindad).res[E.k].sd <= CASI_UNO * sd0;", "const casiUno = E => true;"),
    ("la cuenta del paso 2 vuelve a escribirse con «=»", REZAGO,
     "cu.nb.length + ' ≈ <strong>'", "cu.nb.length + ' = <strong>'"),
    ("el paso 3 vuelve a dar por seguro que W² cuenta a todos los vecinos de siempre", REZAGO,
     "y, casi siempre, a sus vecinos de siempre", "y a sus vecinos de siempre"),
    ("la flecha derecha no da la vuelta al último barrio", REZAGO,
     "case 'ArrowRight': return { foco: (E.foco + 1) % n };", "case 'ArrowRight': return { foco: E.foco + 1 };"),
    ("cada capa se pinta con su propia escala de color", REZAGO,
     "ctx.fillStyle = colorDe(t01(valorVisible(S, i, V.k)));",
     "ctx.fillStyle = colorDe((valorVisible(S, i, V.k) - Math.min.apply(null, S.capas[Math.round(V.k)])) / "
     "(Math.max.apply(null, S.capas[Math.round(V.k)]) - Math.min.apply(null, S.capas[Math.round(V.k)])));"),
    ("la lupa no acerca: la caja es siempre el mapa entero", REZAGO,
     "const caja = sig.lupa ? cajaFoco(sig.foco, sig.vecindad) : cq;", "const caja = cq;"),
    ("la caja de la lupa deja fuera a los vecinos del barrio en foco", REZAGO,
     "const idx = [foco].concat(de(vecindad).vec[foco]);", "const idx = [foco];"),
    ("los números de los vecinos no se separan (se pisan)", REZAGO,
     "return separaEtiquetas(cu.nb.map(j => centro(a, j)), ETQ.w,", "return (x => x)(cu.nb.map(j => centro(a, j)), ETQ.w,"),
    ("las etiquetas separadas se pueden salir del mapa", REZAGO,
     "const dentro = (x, y) => lim ? [", "const dentro = (x, y) => false ? ["),
    ("el clic ignora la caja que se ve y usa siempre la del mapa entero", REZAGO,
     "const a = ajusteDe(c.w, c.h, V && cajaDe(V));", "const a = ajusteDe(c.w, c.h);"),
    # --- la máquina ---
    ("poner acepta NaN, infinitos y texto en una clave numérica", NUCLEO,
     "if (typeof E[k] === 'number' && !(typeof v === 'number' && isFinite(v))) continue;", ""),
    ("poner acepta claves que el estado no tiene", NUCLEO,
     "if (!(k in E)) continue;", ""),
    ("la transición no llega a su destino", NUCLEO,
     "if (a.t >= 1) { V[k] = a.hasta; delete tw[k]; }", "if (a.t >= 1) { V[k] = a.desde; delete tw[k]; }"),
    ("un gesto del usuario no interrumpe el guion", NUCLEO,
     "if (!opc.desdeGuion) pausar();", ""),
    ("el guion no se detiene en el último paso", NUCLEO,
     "if (E.paso < pasos.length) {", "if (E.paso <= pasos.length) {"),
    ("reproducir no vuelve a empezar al final del guion", NUCLEO,
     "const desde = E.paso >= 1 && E.paso < pasos.length ? E.paso : 1;", "const desde = E.paso;"),
    ("las transiciones ignoran prefers-reduced-motion", NUCLEO,
     "if (k in animables && !ganchos.reducido && !opc.corte", "if (k in animables && !opc.corte"),
    ("a la API inerte le falta un método", NUCLEO,
     "avanza: nada, reinicia: nada,", "avanza: nada,"),
    # --- el gesto (revisión del 2026-10-02) ---
    ("un toque vuelve a elegir al bajar el dedo (desplazar la página cambiaba el foco)", NUCLEO,
     "if (ev.tactil) { toque = res && res.poner ? { res, x: ev.x, y: ev.y } : null; return null; }", ""),
    ("salir del lienzo vuelve a interrumpir el guion", NUCLEO,
     "          return con(puntero(ev, E, V, c), false);", "          return con(puntero(ev, E, V, c), true);"),
    ("un toque que se desplazó elige al levantar el dedo", NUCLEO,
     "const elegido = toque && !lejos(ev, toque) ? toque.res : null;", "const elegido = toque ? toque.res : null;"),
    ("pointercancel no anula el toque pendiente", NUCLEO,
     "toque = null; arrastre = false;\n          return null;", "arrastre = false;\n          return null;"),
    ("con el dedo, pasar por encima vuelve a marcar", NUCLEO,
     "if (ev.tactil && !arrastre) return null;", ""),
    ("un paso cuyo estado es una función no se evalúa", NUCLEO,
     "const est = typeof p.estado === 'function' ? p.estado(E) : p.estado;", "const est = p.estado;"),
    # --- la auditoría de las cinco animaciones (2026-10-02) ---
    ("el guion vuelve a no dar tiempo a leer el paso", NUCLEO,
     "Math.max(p.pausa != null ? p.pausa : PAUSA_PASO, lectura(p))", "(p.pausa != null ? p.pausa : PAUSA_PASO)"),
]


def corre(extra_env: dict[str, str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(extra_env)
    return subprocess.run([sys.executable, str(PRUEBA)], capture_output=True, text=True, env=env)


def main() -> int:
    print("\n=== prueba_mutaciones_anim2d.py ===")
    base = corre({})
    if base.returncode != 0:
        print("PARADO: la prueba no pasa con el motor intacto; no tiene sentido romperlo.")
        print(base.stdout[-1500:])
        return 2
    print(f"  intacto: la prueba pasa ({base.stdout.count('  OK  ')} comprobaciones)")
    cazadas = 0
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, archivo, busca, pone in MUTACIONES:
            texto = archivo.read_text(encoding="utf-8")
            if texto.count(busca) != 1:
                print(f"PARADO: «{nombre}»: el texto a sustituir aparece {texto.count(busca)} veces en {archivo.name}")
                return 2
            copia = Path(tmp) / archivo.name
            copia.write_text(texto.replace(busca, pone), encoding="utf-8")
            var = "REZAGO2D_MOTOR" if archivo == REZAGO else "ANIM2D_NUCLEO"
            r = corre({var: str(copia)})
            malas = [l.strip() for l in r.stdout.splitlines() if l.startswith("  MAL")]
            caza = r.returncode != 0
            cazadas += caza
            if malas:
                detalle = malas[0][5:].strip()
            else:                                    # la prueba paró con una excepción: que se vea cuál
                err = [l for l in r.stderr.splitlines() if "Error" in l or l.startswith("PARADO")]
                detalle = (err or ["la prueba paró"])[0]
            detalle = detalle if caza else ""
            print(("  CAZADA  " if caza else "  SE COLÓ ") + nombre + (f"\n            ↳ {detalle[:150]}" if detalle else ""))
    print(f"\n  {cazadas} de {len(MUTACIONES)} defectos cazados")
    if cazadas != len(MUTACIONES):
        print("  HAY DEFECTOS QUE PASAN INADVERTIDOS.\n")
        return 1
    print("  La prueba los caza todos.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
