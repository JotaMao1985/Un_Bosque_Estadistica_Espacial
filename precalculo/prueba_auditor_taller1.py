#!/usr/bin/env python3
"""
prueba_auditor_taller1.py — le rompe el precálculo al auditor del taller (C4)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_1_Caps_1_2.md.

POR QUÉ EXISTE. `audita_taller1.py` informó **431 comprobaciones, 0
fallos** la primera vez que corrió limpio, y ese número no significa nada
por sí solo: un auditor cuyo silencio no se ha interrogado no es un
auditor verificado. Es la lección que este proyecto ya pagó dos veces
—cinco auditores de DOE que jamás miraron dentro de KaTeX, y dos
comprobaciones de T0.5 que eran **incapaces de fallar**—.

Y aquí pesa más que en un capítulo: de estas cifras salen doce notas. Un
auditor que se calle sobre el taller no deja un capítulo con una errata,
deja a un estudiante calificado sobre un dato falso.

CÓMO FUNCIONA. Copia los dos JSON, mete en la copia un defecto concreto,
ejecuta el auditor apuntando a la copia con sus variables de entorno y
exige código distinto de cero. **Los publicados no se tocan nunca**, y al
final se comprueba byte a byte que siguen igual.

LAS DOS REGLAS DEL ARNÉS, heredadas de `prueba_auditor_cap1.py`:

  1. Cada tanda empieza y acaba con un CONTROL sin inyectar nada. Si el
     auditor no sale limpio sobre el original, cualquier «acierto»
     posterior es falso.
  2. «N de N» no basta: se cuenta también cuántas comprobaciones
     DISTINTAS se han visto fallar alguna vez.

LAS FAMILIAS DE DEFECTO. Las cinco primeras son las de los capítulos; las
tres últimas solo existen aquí, porque solo un taller las tiene:

   1. cifra que deja de cuadrar con la fuente primaria
   2. cifra derivada que deja de cuadrar con las que la generan
   3. relación cualitativa rota (monotonías, órdenes, signos)
   4. formato: NaN, decimales de más, tildes en bytes crudos
   5. geometría del .geomapa alterada
   6. LA RESPUESTA SE FILTRA al JSON publicado          ← propio del taller
   7. LA EVIDENCIA DE T3 DESAPARECE, y la tarea se queda sin solución
   8. EL REPARTO se rompe y dos estudiantes reciben lo mismo

Uso:  python3 precalculo/prueba_auditor_taller1.py
Devuelve 1 si algún defecto se cuela.
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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

# La ÚNICA pieza que este arnés comparte con el de los capítulos, y la
# comparte porque nació aquí y les hacía falta a ellos: el detector de
# rótulos largos. El resto de la maquinaria sigue duplicada a propósito
# —un taller no tiene la forma de un capítulo—, pero tener dos copias de
# esto significaría arreglarlo dos veces la próxima vez.
from prueba_auditor_base import avisa_rotulos_largos  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_taller1.py"

ARCHIVOS = {
    "datos": ("TALLER1_DATOS", "taller1_datos.json"),
    "mapas": ("TALLER1_MAPAS", "taller1_mapas.json"),
}

# El intérprete de geo_env: el auditor necesita geopandas, libpysal, esda
# y pyproj. Se lee de versiones_py.json en vez de darse por sabido.
PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


def defectos() -> list[tuple[str, str, str, object]]:
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D: list[tuple[str, str, str, object]] = []

    def add(nombre, archivo, tipo, accion):
        D.append((nombre, archivo, tipo, accion))

    def obj(nombre, archivo, f):
        add(nombre, archivo, "obj", f)

    def txt(nombre, archivo, busca, pone):
        add(nombre, archivo, "txt", (busca, pone))

    # --- 1. Deja de cuadrar con la fuente primaria ----------------------
    obj("el dígito de verificación de un municipio se mueve", "datos",
        lambda o: o["municipios"][0].__setitem__(
            "suma_altitud", o["municipios"][0]["suma_altitud"] + 1))
    obj("un municipio se atribuye a otro departamento", "datos",
        lambda o: o["municipios"][7].__setitem__("departamento", "Vichada"))
    obj("un municipio que no existe en la MGN", "datos",
        lambda o: o["municipios"][3].__setitem__("municipio", "Villa Inventada"))
    obj("una llave de municipio inventada", "datos",
        lambda o: o["municipios"][11].__setitem__("llave", "0000000000000000000000"))
    obj("las estaciones dejan de ser 361", "datos",
        lambda o: o["t7"].__setitem__("n_estaciones", 360))
    obj("la latitud más al norte se falsea", "datos",
        lambda o: o["t7"].__setitem__("lat_max", 11.11))

    # --- 2. Cifra derivada que no cuadra con su origen ------------------
    obj("la R de un patrón deja de ser el cociente de sus dos distancias", "datos",
        lambda o: o["patrones"][4].__setitem__("clark_evans", 1.4713977))
    obj("la distancia esperada bajo CSR deja de salir de lambda", "datos",
        lambda o: o["patrones"][9].__setitem__("nn_esperada", 0.0714913))
    obj("la corrección de Donnelly deja de cuadrar con su fórmula", "datos",
        lambda o: o["patrones"][2].__setitem__("clark_evans_donnelly", 0.9137941))
    obj("lambda deja de ser n partido por el área", "datos",
        lambda o: o["patrones"][15].__setitem__("lambda", 71.4913))
    obj("E[I] deja de ser -1/(n-1)", "datos",
        lambda o: o["t7"].__setitem__("moran_esperado", -0.0031397))
    obj("el cociente de T5 no es el de sus dos medidas", "datos",
        lambda o: o["t5"].__setitem__("veces", 41397.13))
    obj("el grado de longitud en el norte deja de cuadrar con su latitud", "datos",
        lambda o: o["t7"].__setitem__("km_por_grado_lon_norte", 110.4137))
    obj("el error de «111 km por grado» se infla", "datos",
        lambda o: o["t7"].__setitem__("error_grados_pct_mediano", 1.4139771))
    # Este campo nació en C8, cuando `sin_aritmetica.py` cazó las 64 980
    # parejas calculadas EN EL ENSAMBLADOR y se mandaron a R. El auditor
    # ganó su comprobación y este arnés no ganó su ataque: durante C9 el
    # informe lo declaró como el único tipo sin atacar. La cifra sostiene
    # el «0,21 % mediano» de T7, así que un cero a la izquierda de más y
    # el porcentaje se calcula sobre otra población.
    obj("el conteo de parejas que publica R se falsea", "datos",
        lambda o: o["t7"].__setitem__("n_parejas", 64890))

    # --- 3. Relación cualitativa rota -----------------------------------
    obj("corregir el borde deja de BAJAR el índice", "datos",
        lambda o: o["patrones"][6].__setitem__(
            "clark_evans_donnelly", o["patrones"][6]["clark_evans"] + 0.05))
    obj("la brecha esfera/elipsoide deja de superar al error en grados", "datos",
        lambda o: o["t7"].__setitem__("brecha_esfera_elipsoide_pct_mediana", 0.01))
    obj("el buffer de 500 «metros» deja de tragarse a todos", "datos",
        lambda o: o["t5"].__setitem__("en_buffer_500", 3))
    # 9999 y no 11 108: la primera versión de esta inyección dejaba el
    # cociente POR ENCIMA de los cuatro órdenes, así que la comprobación
    # que pretendía atacar seguía pasando. Lo destapó la lista de tipos sin
    # atacar, no la lectura del código.
    obj("el disparate de T5 deja de ser de cuatro órdenes de magnitud", "datos",
        lambda o: (o["t5"].__setitem__("d_declarada_m",
                                       o["t5"]["d_real_km"] * 1000 / 9999.0),
                   o["t5"].__setitem__("veces", 9999.0)))
    obj("el error en grados se publica negativo", "datos",
        lambda o: o["t7"].__setitem__("error_grados_pct_mediano", -0.5))
    obj("aparece una sección de más en la raíz del JSON", "datos",
        lambda o: o.__setitem__("borrador", {"pendiente": "revisar"}))
    obj("un mapa se desborda del presupuesto de geometría", "mapas",
        lambda o: o["patron-20"].__setitem__("pts", o["patron-20"]["pts"] * 4000))

    # --- 4. Formato ------------------------------------------------------
    txt("una tilde convertida en bytes crudos", "datos",
        "Bolívar", "Bol<c3><ad>var")
    txt("un flotante con más decimales de los declarados", "datos",
        '"error_grados_pct_max"', '"error_grados_pct_max_x": 0.123456789012345, "error_grados_pct_max"')
    txt("un NaN escondido en las cifras de un patrón", "datos",
        '"nn_media"', '"nn_media_x": NaN, "nn_media"')

    # --- 5. El .geomapa ---------------------------------------------------
    obj("el n declarado de un mapa deja de ser el de su ficha", "mapas",
        lambda o: o["patron-03"].__setitem__("n", 999))
    obj("un mapa se dibuja con los puntos de otro patrón", "mapas",
        lambda o: o["patron-05"].__setitem__("pts", o["patron-12"]["pts"]))
    obj("la cuantización declarada no es una de las del componente", "mapas",
        lambda o: o["patron-08"].__setitem__("q", 3000))
    # LA HERMANA DE LA DE ARRIBA, y la añadió el propio informe de este arnés.
    # Las dos comprobaciones de la q son distintas: una mira que las
    # coordenadas no se SALGAN de la q, y ésta que la LLENEN. Sin la segunda,
    # un mapa quantizado de verdad a 1024 y declarado a 4096 pasa limpio: no
    # se sale de nada, y se dibuja en una esquina del lienzo. Hasta el
    # 2026-08-24 nadie la atacaba, y no se veía porque el rótulo era largo y
    # el recuento de tipos la daba por cubierta; en cuanto el rótulo cupo, el
    # informe la nombró. Es la misma historia que el `n_parejas` de C9: lo que
    # destapa la deuda es que el arnés diga en voz alta lo que NO ataca.
    #
    # Encoger las coordenadas mueve también d_min, así que esto lo caza además
    # el contraste mapa-contra-cifras. No es un defecto de la inyección: es
    # que un mapa así está mal por dos motivos a la vez.
    obj("un mapa declara una q que sus coordenadas no llenan", "mapas",
        lambda o: o["patron-11"].__setitem__(
            "pts", [int(v * 0.3) for v in o["patron-11"]["pts"]]))
    obj("la caja de un mapa queda desordenada", "mapas",
        lambda o: o["patron-02"].__setitem__("caja", [1.0, 1.0, 0.0, 0.0]))

    # --- 6. LA RESPUESTA SE FILTRA (propio de un taller) -----------------
    # Es el defecto que ningún auditor de capítulo puede tener y el que más
    # daño haría: el JSON viaja dentro del HTML, así que un campo añadido
    # «para depurar» deja el taller resuelto en el código fuente.
    obj("la familia del patrón se cuela en el JSON publicado", "datos",
        lambda o: o["patrones"][0].__setitem__("familia", "mixto"))
    obj("alguien anota cuál de los dos correlogramas es el bueno", "datos",
        lambda o: o["t3"].__setitem__("nota", "el correcto es A"))
    obj("un municipio publica el área que T4 pide calcular", "datos",
        lambda o: o["municipios"][2].__setitem__("area_3116_km2", 137.41))

    # --- 7. LA EVIDENCIA DE T3 DESAPARECE --------------------------------
    # Sin la identidad de sumas acumuladas, T3 no tiene forma de resolverse
    # y el estudiante que la busque bien no la encontrará. Un taller sin
    # respuesta es peor que un taller con una errata.
    obj("los conteos de parejas dejan de ser la suma acumulada", "datos",
        lambda o: o["t3"]["B"][3].__setitem__(
            "n_pares", o["t3"]["B"][3]["n_pares"] + 10))
    obj("la primera banda deja de ser idéntica en los dos", "datos",
        lambda o: o["t3"]["A"][0].__setitem__("I", 0.6414))
    obj("el correlograma sembrado deja de decaer, y se ve roto", "datos",
        lambda o: o["t3"]["B"][2].__setitem__("I", 0.9137))
    obj("las estaciones sin vecino de una banda se falsean", "datos",
        lambda o: o["t3"]["A"][1].__setitem__("sin_vecinos", 40))

    # --- 8. EL REPARTO se rompe -------------------------------------------
    obj("dos documentos reciben exactamente la misma variante", "datos",
        lambda o: (o["variantes"]["m0"].__setitem__(5, o["variantes"]["m0"][6]),
                   o["variantes"]["p0"].__setitem__(5, o["variantes"]["p0"][6])))
    obj("un municipio del catálogo no le toca a nadie", "datos",
        lambda o: [o["variantes"]["m0"].__setitem__(i, 0)
                   for i, v in enumerate(o["variantes"]["m0"]) if v == 59])
    obj("un índice apunta fuera del catálogo", "datos",
        lambda o: o["variantes"]["p0"].__setitem__(0, 99))
    obj("el reparto deja de declarar su base", "datos",
        lambda o: o["variantes"].__setitem__("base", 1))
    obj("faltan filas en la tabla de variantes", "datos",
        lambda o: o["variantes"].__setitem__("m0", o["variantes"]["m0"][:-3]))
    obj("las dos columnas del reparto dejan de medir lo mismo", "datos",
        lambda o: o["variantes"].__setitem__("p0", o["variantes"]["p0"][:-5]))
    obj("dos municipios comparten llave", "datos",
        lambda o: o["municipios"][9].__setitem__("llave", o["municipios"][8]["llave"]))

    # --- 9. T6, la fuga espacial -----------------------------------------
    obj("la CV por bloques deja de salir peor que la aleatoria", "datos",
        lambda o: o["t6"].__setitem__("rmse_bloques", o["t6"]["rmse_aleatoria"] - 1.0))
    obj("el R2 de la CV aleatoria no sale de su RMSE", "datos",
        lambda o: o["t6"].__setitem__("r2_aleatoria", 0.7139771))
    obj("los pliegues espaciales dejan de sumar n", "datos",
        lambda o: o["t6"]["tam_pliegues"].__setitem__(0, 1))
    obj("hay menos pliegues de los que se declaran", "datos",
        lambda o: o["t6"].__setitem__("tam_pliegues", o["t6"]["tam_pliegues"][:-1]))
    obj("los municipios con puntaje dejan de ser los del CSV", "datos",
        lambda o: o["t6"].__setitem__("n", 1100))
    obj("la desviación del puntaje se falsea", "datos",
        lambda o: o["t6"].__setitem__("sd_variable", 19.4137))

    # --- 10. Los que faltaban por atacar, uno por tipo -------------------
    # Esta tanda no nació de imaginar defectos nuevos: nació de la lista
    # que el propio arnés imprime al final —«tipos que todavía no ataca»—.
    # Sin esa lista, la cobertura por tipos se habría quedado en 42 de 81 y
    # el informe habría dicho «37 de 37» tan campante.
    obj("el meta declara más municipios de los que hay", "datos",
        lambda o: o["meta"].__setitem__("n_municipios", 61))
    obj("el meta declara más patrones de los que hay", "datos",
        lambda o: o["meta"].__setitem__("n_patrones", 31))
    obj("T3 declara un número de bandas que no tiene", "datos",
        lambda o: o["t3"].__setitem__("bandas", 7))
    obj("el municipio del ejemplo de T5 no existe en la MGN", "datos",
        lambda o: o["t5"].__setitem__("municipio", "Ciudad Imaginaria"))
    obj("la caja declarada de T5 se falsea por el oeste", "datos",
        lambda o: o["t5"]["caja_declarada"].__setitem__(0, -80.0))
    obj("la caja declarada de T5 se falsea por el norte", "datos",
        lambda o: o["t5"]["caja_declarada"].__setitem__(3, 9.99))
    obj("los km reales de T5 dejan de ser los de la esfera de s2", "datos",
        lambda o: o["t5"].__setitem__("d_real_km", 31.4159265))
    obj("los «metros» de la declaración falsa se falsean", "datos",
        lambda o: o["t5"].__setitem__("d_declarada_m", 0.3141593))
    obj("la latitud más al sur se falsea", "datos",
        lambda o: o["t7"].__setitem__("lat_min", -2.22))
    obj("el error máximo en grados se falsea", "datos",
        lambda o: o["t7"].__setitem__("error_grados_pct_max", 4.1397713))
    obj("el máximo de la brecha esfera/elipsoide se falsea", "datos",
        lambda o: o["t7"].__setitem__("brecha_esfera_elipsoide_pct_max", 1.4139771))
    obj("el grado de longitud en el sur deja de cuadrar", "datos",
        lambda o: o["t7"].__setitem__("km_por_grado_lon_sur", 109.4137))
    obj("el radio de la esfera de s2 deja de ser el de s2", "datos",
        lambda o: o["t7"].__setitem__("radio_esfera_s2_m", 6371000.0))
    obj("desaparece el mapa de un patrón", "mapas",
        lambda o: o.pop("patron-07"))
    obj("un mapa declara un modo que el componente no conoce", "mapas",
        lambda o: o["patron-11"].__setitem__("modo", "burbujas"))
    obj("un mapa declara una codificación inventada", "mapas",
        lambda o: o["patron-14"].__setitem__("codificacion", "comprimida"))
    txt("un NaN escondido en un mapa", "mapas",
        '"modo"', '"modo_x": NaN, "modo"')

    return D


def corre(rutas: dict[str, pathlib.Path]) -> tuple[int, str]:
    entorno = dict(os.environ)
    for clave, ruta in rutas.items():
        entorno[ARCHIVOS[clave][0]] = str(ruta)
    res = subprocess.run([PY, str(AUDITOR)], capture_output=True, text=True,
                         cwd=str(RAIZ), env=entorno)
    return res.returncode, res.stdout + res.stderr


def resumen(salida: str) -> str:
    m = re.search(r"(\d+) comprobaciones · (\d+) fallos", salida)
    return m.group(0) if m else "(sin resumen — el auditor ni siquiera llegó al cierre)"


def nombres(salida: str, estado: str) -> set[str]:
    fuera = set()
    for linea in salida.splitlines():
        m = re.match(r"\s{2}" + re.escape(estado) + r"\s{2,}(\S.*?)\s{2,}", linea + "  ")
        if m:
            fuera.add(m.group(1).strip())
    return fuera


def main() -> int:
    for _, nombre in ARCHIVOS.values():
        if not (SALIDAS / nombre).exists():
            print(f"PARADO: falta {SALIDAS / nombre}. Ejecuta antes "
                  f"precalculo/rscript.sh precalculo/genera_taller1.R")
            return 1

    originales = {c: (SALIDAS / n).read_bytes() for c, (_, n) in ARCHIVOS.items()}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="prueba_auditor_taller1_"))
    limpias = {}
    for clave, (_, nombre) in ARCHIVOS.items():
        limpias[clave] = tmp / nombre
        shutil.copy(SALIDAS / nombre, limpias[clave])

    print("=" * 70)
    print("  prueba_auditor_taller1.py — el arnés de inyección del Taller 1")
    print("=" * 70)

    codigo, salida = corre(limpias)
    print(f"\n  {'OK ' if codigo == 0 else 'MAL'}  control de entrada · sin inyectar nada")
    print(f"        {resumen(salida)}")
    if codigo != 0:
        print("\n  PARADO: el control falla, así que el arnés no prueba nada.")
        for linea in salida.strip().splitlines():
            if linea.strip().startswith("- "):
                print(f"        {linea.strip()}")
        return 1

    todas = nombres(salida, "OK ")
    vistas_fallar: set[str] = set()

    # El detector de rótulos largos vive en `prueba_auditor_base.py` desde
    # el 2026-08-24. Nació aquí —éste era el único arnés que contaba TIPOS
    # y por eso el único que notaba el defecto—, y se subió al núcleo en
    # cuanto se vio que los cuatro capítulos tenían el mismo agujero sin
    # nadie mirándolo: 83 rótulos largos en el 1, 69 en el 2, 12 en el 3.
    avisa_rotulos_largos(todas)

    lista = defectos()
    cazados = 0
    print(f"\n  {len(lista)} defectos que inyectar\n" + "-" * 70)

    for nombre_d, clave, tipo, accion in lista:
        rutas = dict(limpias)
        rota = tmp / f"roto_{ARCHIVOS[clave][1]}"
        if tipo == "obj":
            crudo = limpias[clave].read_text(encoding="utf-8")
            o = json.loads(crudo)
            antes = json.dumps(o, ensure_ascii=False, sort_keys=True)
            accion(o)
            despues = json.dumps(o, ensure_ascii=False, sort_keys=True)
            if antes == despues:
                # Una inyección inerte registraría un «no detectado» que es
                # culpa del arnés y no del auditor. Se distingue.
                print(f"  MAL  {nombre_d}")
                print("        INERTE · la mutación no cambió el archivo")
                continue
            rota.write_text(json.dumps(o, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        else:
            busca, pone = accion
            t = limpias[clave].read_text(encoding="utf-8")
            if busca not in t:
                print(f"  MAL  {nombre_d}")
                print(f"        INERTE · no aparece el texto a sustituir: {busca[:50]!r}")
                continue
            rota.write_text(t.replace(busca, pone, 1), encoding="utf-8")
        rutas[clave] = rota

        codigo, salida = corre(rutas)
        ok = codigo != 0
        cazados += ok
        print(f"  {'OK ' if ok else 'MAL'}  {nombre_d}")
        print(f"        {resumen(salida)}")
        vistas_fallar |= nombres(salida, "MAL")

    # --- CONTROL DE SALIDA -------------------------------------------
    codigo, salida = corre(limpias)
    print("-" * 70)
    print(f"  {'OK ' if codigo == 0 else 'MAL'}  control de salida · el arnés no dejó nada tocado")
    intactos = all((SALIDAS / n).read_bytes() == originales[c]
                   for c, (_, n) in ARCHIVOS.items())
    print(f"  {'OK ' if intactos else 'MAL'}  los JSON publicados siguen byte a byte igual")

    # El recuento crudo engaña, y hay que decir por qué. El auditor repite
    # la misma comprobación 30 veces —una por patrón— y 12 veces —una por
    # banda y lado—: contar instancias da un «375 nunca vistas fallar» que
    # asusta sin informar, porque atacar el patrón 5 prueba exactamente lo
    # mismo que atacar el 23. Lo que hay que cubrir son los TIPOS. Se
    # informan los dos números, y el que manda es el segundo.
    def tipo(n: str) -> str:
        n = re.sub(r"patrón \d+", "patrón NN", n)
        n = re.sub(r"patron-\d+", "patron-NN", n)
        n = re.sub(r"T3/[AB] \d+-\d+ km", "T3/banda", n)
        # Las doce palabras prohibidas son doce instancias de una sola
        # comprobación: atacar «mixto» prueba lo mismo que atacar «regular».
        n = re.sub(r"el JSON publicado no contiene «.*»",
                   "el JSON publicado no contiene una palabra prohibida", n)
        return n

    # Hay comprobaciones que este arnés NO PUEDE atacar por construcción,
    # y no es una laguna: contrastan los JSON contra los GeoPackage, y el
    # arnés solo envenena los JSON. Romperlas exigiría tocar las fuentes,
    # que es justo lo que un arnés no debe hacer. Se listan aparte para no
    # contarlas como deuda ni esconderlas como cubiertas.
    SOLO_FUENTES = {
        "municipios que lee geopandas",
        "estaciones que lee geopandas",
        "las capas llegan en EPSG:9377 también por este camino",
        # Las dos partes de esta igualdad se calculan aquí desde el
        # GeoPackage: el JSON no interviene, así que envenenarlo no la
        # mueve.
        "T7: las 64 980 parejas de estaciones",
    }

    tipos_todos = {tipo(x) for x in todas} - SOLO_FUENTES
    tipos_vistos = {tipo(x) for x in vistas_fallar} & tipos_todos
    tipos_nunca = sorted(tipos_todos - tipos_vistos)

    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(lista)} defectos cazados")
    print(f"  instancias: {len(vistas_fallar)} de {len(todas)} se han visto fallar")
    print(f"  TIPOS:      {len(tipos_vistos)} de {len(tipos_todos)} se han visto fallar")
    print(f"  ({len(SOLO_FUENTES)} tipos más solo pueden fallar si cambian los "
          f"GeoPackage, y el arnés no los toca)")
    if tipos_nunca:
        # Una comprobación que nunca ha fallado puede estar bien escrita o
        # ser incapaz de fallar, y desde fuera se ven igual. Por eso los
        # tipos sin atacar se listan ENTEROS: son la lista de trabajo del
        # próximo que toque este arnés, no una nota al pie.
        print(f"\n  {len(tipos_nunca)} tipo(s) que este arnés todavía no ataca:")
        for t in tipos_nunca:
            print(f"      · {t}")
    print("=" * 70)
    return 0 if (cazados == len(lista) and codigo == 0 and intactos) else 1


if __name__ == "__main__":
    sys.exit(main())
