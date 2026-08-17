#!/usr/bin/env python3
"""
sin_aritmetica.py — ninguna cifra de la prosa se calcula en el ensamblador

Material de Estadística Espacial 2026-II (20929). T2.2.

POR QUÉ EXISTE. D10 dice «ninguna cifra a mano»: todo número que el capítulo
publica sale de R. `audita_texto_capN.py` lo vigila por el resultado —¿existe
esta cifra en el JSON?— y esa vigilancia tiene un agujero medido: su índice
tiene más de cien mil entradas, así que **una cifra de pocos decimales cae
dentro por azar**. El «61.7» del capítulo 1 vivió ahí meses: lo calculaba el
ensamblador con `n(factor ** 2, 1)`, no existía en ningún JSON, y los dos
auditores daban verde. Se encontró en T2.2, y no mirando cifras sino mirando
el código que las escribe.

Este guion mira la CAUSA, y con `ast` la detección es exacta: o hay una
operación aritmética dentro de un formateador, o no la hay. No hay índice, no
hay azar, no hay tolerancia.

POR QUÉ NO ESTÁ DENTRO DE CADA ENSAMBLADOR. Porque serían tres copias de la
misma comprobación —cinco cuando lleguen los capítulos 4 y 5—, y con copias un
arreglo se hace en un sitio y se olvida en los otros. Es la lección que
`audita_texto_base.py` aprendió en T0.5 y `audita_base.py` en T2.1d.

LA EXCEPCIÓN, que es de fondo y no una comodidad. Dentro de un **bloque de
código** sí se puede calcular. Ahí la línea `#>` no es una afirmación del
autor: es la salida que el lector va a obtener al ejecutar, y
`verifica_bloques.py` **ejecuta de verdad** los bloques de los tres capítulos
y contrasta las cifras anunciadas contra la salida real —297 de 297 el
2026-08-07—. Eso es una garantía más fuerte que el JSON, no más débil. En la
prosa no hay nada que ejecute, y por eso ahí la regla es absoluta. Las
exenciones se **cuentan y se imprimen**, para que no sean tácitas.

Uso:  python3 precalculo/sin_aritmetica.py
      python3 precalculo/sin_aritmetica.py --prueba   (se rompe a sí mismo)
Devuelve 1 si alguna cifra de la prosa se calcula fuera de R.
"""
from __future__ import annotations

import ast
import pathlib
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"

# Las funciones que convierten un número en el texto que se publica. Si un
# capítulo estrena otra, hay que añadirla aquí — y el guion lo dice solo: la
# comprobación de abajo exige que las cuatro sigan existiendo en cada
# ensamblador, así que renombrar una sin tocar esta lista se ve.
FORMATEADORES = {"n", "n5", "ent", "ent_mate"}
# Las funciones que envuelven un bloque de código ejecutable.
BLOQUES_DE_CODIGO = {"tabs"}
ARITMETICA = (ast.Div, ast.Mult, ast.Sub, ast.Add, ast.Pow, ast.Mod, ast.FloorDiv)


def revisa(ruta: pathlib.Path) -> tuple[list[str], int, set[str]]:
    """(cifras calculadas en la prosa, exentas por bloque, formateadores vistos)."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    # Los nodos que cuelgan de un `tabs(...)`: se marcan por identidad, que es
    # lo único estable — el número de línea de un nodo anidado no basta para
    # saber de quién cuelga.
    en_bloque: set[int] = set()
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                and nodo.func.id in BLOQUES_DE_CODIGO):
            en_bloque.update(id(x) for x in ast.walk(nodo))

    culpables, exentas, vistos = [], 0, set()
    for nodo in ast.walk(arbol):
        if not (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                and nodo.func.id in FORMATEADORES and nodo.args):
            continue
        vistos.add(nodo.func.id)
        if not any(isinstance(x, ast.BinOp) and isinstance(x.op, ARITMETICA)
                   for x in ast.walk(nodo.args[0])):
            continue
        if id(nodo) in en_bloque:
            exentas += 1
            continue
        culpables.append(f"{ruta.name}:{nodo.lineno}  {ast.unparse(nodo)[:78]}")
    return culpables, exentas, vistos


# Los ensamblados que NO son material del curso: fixtures del arnés, que
# existen para romperse. Se nombran uno a uno —lista corta y explícita—
# en vez de excluirse con un patrón, porque un patrón se lleva por delante
# lo que no debe el día que alguien nombra un archivo parecido.
NO_SON_MATERIAL = {"ensambla_demo_auditoria.py"}


def ensambladores() -> list[pathlib.Path]:
    """Todos los ensambladores de material, descubiertos y no listados.

    Con una lista, el capítulo 4 nacería sin esta comprobación y nadie se
    enteraría hasta que alguien la echara de menos.

    EL PATRÓN SE AMPLIÓ EN C8 DEL TALLER 1, y por lo mismo que existe esta
    función. Buscaba `ensambla_cap*.py`, así que `ensambla_taller1.py`
    —2 000 líneas de prosa con cifras interpoladas— quedaba fuera de la
    única comprobación que mira la CAUSA del defecto del 61.7. El taller
    habría nacido sin ella y el informe habría seguido diciendo «3
    ensambladores revisados» tan campante.
    """
    return sorted(p for p in PRECALCULO.glob("ensambla_*.py")
                  if p.name not in NO_SON_MATERIAL)


def barre(rutas: list[pathlib.Path], verboso: bool = True) -> int:
    fallos = 0
    for ruta in rutas:
        culpables, exentas, vistos = revisa(ruta)
        estado = "OK " if not culpables else "MAL"
        if verboso:
            print(f"  {estado}  {ruta.name:<22} "
                  f"{len(culpables)} en la prosa · {exentas} exenta(s) en bloques de "
                  f"código · formateadores usados: {sorted(vistos)}")
            for c in culpables:
                print(f"         {c}")
        fallos += len(culpables)
    return fallos


def prueba() -> int:
    """Se rompe a sí mismo: una comprobación que nadie ha visto fallar puede
    estar bien escrita o ser incapaz de fallar, y desde fuera se ven igual.

    Se inyecta sobre una COPIA, nunca sobre el original, y se comprueba
    además que la inyección de verdad cambió el archivo: una sustitución
    inerte y una guarda que se cuela se ven exactamente igual desde el
    resultado.
    """
    print("\n=== Autoprueba: se le inyecta el defecto del 61.7 ==========")
    original = ensambladores()[0]
    texto = original.read_text(encoding="utf-8")
    casos = [
        # (nombre, línea que se añade, si tiene que cazarse)
        ("una división en la prosa",
         '\nBASURA_T22 = f"""<p>{n(inf["n"] / inf["k"])}</p>"""\n', True),
        ("un cuadrado en la prosa",
         '\nBASURA_T22 = f"""<p>{n(inf["k"] ** 2)}</p>"""\n', True),
        ("la misma aritmética DENTRO de un bloque de código",
         '\nBASURA_T22 = tabs("x", "#> " + n(inf["n"] / inf["k"]), "y")\n', False),
    ]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="sin_aritmetica_"))
    fallos = 0
    limpio, _, _ = revisa(original)
    if limpio:
        print(f"  MAL  el control no está limpio: {limpio}")
        return 1
    print(f"  OK   control · {original.name} sale limpio sin inyectar nada")
    for nombre, linea, debe_cazarse in casos:
        copia = tmp / original.name
        copia.write_text(texto + linea, encoding="utf-8")
        if copia.read_text(encoding="utf-8") == texto:
            print(f"  MAL  INERTE · «{nombre}» no cambió el archivo")
            fallos += 1
            continue
        culpables, exentas, _ = revisa(copia)
        cazado = bool(culpables)
        ok = cazado == debe_cazarse
        que = "cazado" if cazado else ("exento" if exentas else "SE COLÓ")
        print(f"  {'OK ' if ok else 'MAL'}  «{nombre}» → {que}"
              + ("" if debe_cazarse else "  (tiene que quedar exento)"))
        fallos += 0 if ok else 1
    return fallos


def main(argv: list[str]) -> int:
    print("\n=== sin_aritmetica.py · ninguna cifra de la prosa se calcula "
          "fuera de R ===")
    rutas = ensambladores()
    if not rutas:
        print("  MAL  no se encontró ningún ensambla_cap*.py")
        return 1
    fallos = barre(rutas)
    if "--prueba" in argv:
        fallos += prueba()
    print()
    if fallos:
        print(f"  {fallos} problema(s).\n")
        return 1
    print(f"  {len(rutas)} ensambladores revisados · ninguna cifra de la prosa "
          f"se calcula fuera de R.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
