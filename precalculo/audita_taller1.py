#!/usr/bin/env python3
"""
audita_taller1.py — auditoría independiente del precálculo del Taller 1 (C3)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_1_Caps_1_2.md.

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R. Mismo motivo que en los capítulos —un
control que comparte entorno con lo que audita no es independiente— y aquí
importa más que en ningún otro sitio: de estas cifras salen las notas de
doce personas.

QUÉ COMPRUEBA, Y POR QUÉ CADA COSA

  1. QUE NO SE FILTRE LA RESPUESTA. Es la comprobación propia de un
     taller y no existe en ningún auditor de capítulo. El JSON viaja
     entero dentro del HTML: si algún día alguien añade al generador el
     campo `familia` «para depurar», el taller queda resuelto en el código
     fuente de la página y nadie se entera. Aquí se para.
  2. EL CATÁLOGO, rehecho desde los GeoPackage con geopandas: que los 60
     municipios existan, que su departamento sea el que dice el cruce
     espacial, y que el dígito de verificación de las 40 estaciones se
     reproduzca aplicando la regla publicada.
  3. LOS PATRONES, por dos caminos: la coherencia interna de las cuatro
     cifras (exacta) y el contraste contra el mapa cuantizado que el
     estudiante va a VER (con la tolerancia de la cuantización). Lo
     segundo cierra el hueco donde el material ya se quemó una vez: que
     las cifras y el dibujo sean de patrones distintos no lo ve nadie.
  4. LAS SALIDAS SEMBRADAS. Que el correlograma defectuoso sea de verdad
     el acumulado —recalculado aquí con libpysal— y que la evidencia que
     T3 pide encontrar exista en las cifras publicadas.
  5. EL REPARTO: 1000 parejas distintas, en base cero, sin huecos.

LA CONVENCIÓN QUE NO SE PUEDE ESQUIVAR, heredada de `audita_cap1.py`:
`spdep::moran.test` con `zero.policy = TRUE` toma n = unidades CON
vecinos y `esda.Moran` toma n = todas. En la primera banda del taller son
75 estaciones sin vecino de 361, así que la diferencia está en la segunda
cifra. Las dos convenciones se convierten exactamente una en otra, y por
eso el JSON publica `sin_vecinos` por banda: sin ese entero esta
comprobación habría que declararla saltada.

Uso:  python3 precalculo/audita_taller1.py    (desde `Estadistica espacial/`)
Con el intérprete de geo_env. Devuelve 1 si algo falla.

TALLER1_DATOS y TALLER1_MAPAS permiten apuntar a copias con defectos
inyectados, que es lo que hará `prueba_auditor_taller1.py` en C4. Los
archivos publicados no se tocan nunca.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"

from audita_base import Auditoria, audita_geomapa, carga, decimales, sin_nan  # noqa: E402

# Las palabras que NO pueden aparecer en el JSON publicado. Cada una es la
# respuesta de una tarea: la familia del patrón (T1) y cuál de los dos
# correlogramas está mal (T3).
PROHIBIDAS = ("familia", "agregado", "regular", "mixto", "aleatorio", "regimen",
              "régimen", "correcto", "defectuoso", "acumulad", "sembrad", "respuesta")


def main() -> int:
    import geopandas as gpd
    import numpy as np
    from esda.moran import Moran
    from libpysal.weights import W, DistanceBand

    a = Auditoria("Precálculo del Taller 1 verificado")
    D, ruta_d = carga("TALLER1_DATOS", "taller1_datos.json", SALIDAS)
    M, ruta_m = carga("TALLER1_MAPAS", "taller1_mapas.json", SALIDAS)
    print(f"\n=== audita_taller1.py · {ruta_d.name} + {ruta_m.name} ===")

    meta = D["meta"]
    n_mun = meta["n_municipios"]
    n_pat = meta["n_patrones"]
    n_var = meta["n_variantes"]
    n_est_regla = meta["n_estaciones"]

    # -----------------------------------------------------------------
    a.titulo("Que no se filtre ninguna respuesta")
    crudo = ruta_d.read_text(encoding="utf-8").lower()
    for palabra in PROHIBIDAS:
        a.cierto(palabra not in crudo,
                 f"el JSON publicado no contiene «{palabra}»")
    # TODOS los elementos, no el primero. La versión anterior miraba
    # `[0]` y el arnés de C4 se le coló por ahí: un área publicada en el
    # municipio 3 —justo lo que T4 pide calcular— pasó sin que nadie
    # dijera nada. Es la misma trampa de alcance que en T0.5 dejaba al
    # auditor de prosa comprobando solo el primer bloque de quiz.
    CAMPOS_PATRON = {"n", "area", "lambda", "nn_media", "nn_esperada",
                     "clark_evans", "clark_evans_donnelly"}
    CAMPOS_MUN = {"llave", "municipio", "departamento", "suma_altitud"}
    sobra_pat = sorted({c for p in D["patrones"] for c in set(p) - CAMPOS_PATRON})
    falta_pat = sorted({c for p in D["patrones"] for c in CAMPOS_PATRON - set(p)})
    a.cierto(not sobra_pat and not falta_pat,
             f"de los {len(D['patrones'])} patrones se publican SOLO sus cifras",
             f"sobra {sobra_pat} · falta {falta_pat}")
    sobra_mun = sorted({c for m in D["municipios"] for c in set(m) - CAMPOS_MUN})
    falta_mun = sorted({c for m in D["municipios"] for c in CAMPOS_MUN - set(m)})
    a.cierto(not sobra_mun and not falta_mun,
             f"de los {len(D['municipios'])} municipios, solo identidad y dígito",
             f"sobra {sobra_mun} · falta {falta_mun}")
    # Y las claves de primer nivel, por la misma razón: un `t3.nota` o un
    # `clave` añadido «para depurar» resolvería el taller entero.
    RAIZ_ESPERADA = {"meta", "reglas", "municipios", "patrones", "variantes",
                     "t3", "t5", "t6", "t7"}
    a.cierto(set(D) == RAIZ_ESPERADA,
             "el JSON publica exactamente las nueve secciones previstas",
             str(sorted(set(D) ^ RAIZ_ESPERADA)))
    a.cierto(set(D["t3"]) == {"bandas", "A", "B"},
             "y el bloque de T3 no trae ninguna anotación de más", str(sorted(D["t3"])))

    # -----------------------------------------------------------------
    a.titulo("Formato: sin NaN, con holgura de decimales, sin mojibake")
    a.cierto(not list(sin_nan(D)), "ningún NaN ni infinito en los datos")
    a.cierto(not list(sin_nan(M)), "ningún NaN ni infinito en los mapas")
    pocos = [(r, d) for r, d in decimales(D) if d > 10]
    a.cierto(not pocos, "ningún flotante pasa de diez decimales", str(pocos[:3]))
    a.cierto("<c3>" not in crudo and "<c2>" not in crudo,
             "las tildes llegaron enteras (sin bytes crudos)")

    # -----------------------------------------------------------------
    a.titulo("El catálogo de municipios, rehecho desde el GeoPackage")
    gm = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    gd = gpd.read_file(PROCESADO / "colombia_adm1.gpkg")
    ge = gpd.read_file(PROCESADO / "colombia_estaciones_clima.gpkg")
    a.igual(len(gm), 1122, "municipios que lee geopandas")
    a.igual(len(ge), 361, "estaciones que lee geopandas")
    a.cierto(gm.crs.to_epsg() == 9377 and ge.crs.to_epsg() == 9377,
             "las capas llegan en EPSG:9377 también por este camino")

    cat = D["municipios"]
    a.igual(len(cat), n_mun, "el catálogo trae los municipios que declara")
    a.cierto(len({m["llave"] for m in cat}) == n_mun, "sin llaves repetidas")

    # `representative_point()` de shapely y `st_point_on_surface()` de sf
    # son el mismo algoritmo de GEOS. Si dejaran de serlo, la regla de las
    # 40 estaciones seleccionaría otro conjunto y el dígito de
    # verificación no cuadraría: por eso se comprueba el dígito y no el
    # punto, que es lo que de verdad usa el estudiante.
    gm = gm.set_index("shapeID")
    pos = gm.geometry.representative_point()
    xy_est = np.c_[ge.geometry.x.values, ge.geometry.y.values]
    alt = ge["altitud_m"].to_numpy()
    union_dep = gd.set_index("shapeName").geometry

    malos_dep, malos_sum, malos_nom = [], [], []
    for m in cat:
        if m["llave"] not in gm.index:
            malos_nom.append(m["llave"])
            continue
        if gm.loc[m["llave"], "shapeName"] != m["municipio"]:
            malos_nom.append(m["llave"])
        p = pos.loc[m["llave"]]
        # El departamento, por geometría y no por nombre: es el cruce que
        # hizo R, hecho aquí con otra biblioteca.
        dentro = union_dep[union_dep.contains(p)]
        nombre_dep = dentro.index[0] if len(dentro) else gd.iloc[
            gd.distance(p).idxmin()]["shapeName"]
        if nombre_dep != m["departamento"]:
            malos_dep.append((m["municipio"], m["departamento"], nombre_dep))
        d = np.hypot(xy_est[:, 0] - p.x, xy_est[:, 1] - p.y)
        suma = int(alt[np.argsort(d, kind="stable")[:n_est_regla]].sum())
        if suma != m["suma_altitud"]:
            malos_sum.append((m["municipio"], suma, m["suma_altitud"]))

    a.cierto(not malos_nom, "los 60 existen en adm2 con ese nombre", str(malos_nom[:3]))
    a.cierto(not malos_dep, "el departamento sale del cruce espacial de geopandas",
             str(malos_dep[:3]))
    a.cierto(not malos_sum,
             f"el dígito de verificación reproduce las {n_est_regla} estaciones",
             str(malos_sum[:3]))

    # -----------------------------------------------------------------
    a.titulo("Los patrones: coherencia interna y contraste contra su mapa")
    # Hasta dónde llega la independencia aquí, dicho en voz alta. Los
    # patrones nacen de spatstat, que no tiene equivalente en Python: no se
    # pueden regenerar por otro camino. Lo que sí se comprueba —y no es
    # poco— es que las cuatro cifras sean coherentes entre sí y que
    # describan EL MISMO patrón que el estudiante va a ver dibujado. Lo que
    # queda fuera es la generación misma, que en R ancla `clarkevans()`
    # patrón por patrón.
    a.salta("la generación de los 30 patrones, rehecha por otro camino",
            "spatstat no existe en Python; en R cada patrón se ancla contra "
            "spatstat.explore::clarkevans() y el guion para si no cuadra")
    pats = D["patrones"]
    a.igual(len(pats), n_pat, "el catálogo trae los patrones que declara")
    a.igual(len(M), n_pat, "y hay un mapa por patrón")
    for k, p in enumerate(pats, start=1):
        etq = f"patrón {k:02d}"
        n, area = p["n"], p["area"]
        a.igual(p["lambda"], n / area, f"{etq}: lambda = n/area", 1e-9)
        esperada = 0.5 / math.sqrt(n / area)
        a.igual(p["nn_esperada"], esperada, f"{etq}: E[d] bajo CSR = 1/(2 sqrt(lambda))", 1e-9)
        # 1e-8 y no 1e-9, y el motivo es aritmético y no una concesión: el
        # JSON publica las tres cifras redondeadas a diez decimales POR
        # SEPARADO, así que el cociente de dos redondeadas no es el
        # redondeo del cociente. Con nn_esperada ~ 0.06, medio ulp en el
        # denominador mueve R en 1.5e-9. Se midió: el peor desvío de los
        # treinta es 1.2e-9, y a 1e-9 esta comprobación fallaba en seis
        # patrones sanos.
        a.igual(p["clark_evans"], p["nn_media"] / p["nn_esperada"],
                f"{etq}: R = observada / esperada", 1e-8)
        # Donnelly, con el 0.0412 de spatstat y no el 0.041 que suele
        # citarse; el perímetro de la ventana unidad es 4.
        don = p["nn_media"] / (0.5 * math.sqrt(area / n) +
                               (0.0514 + 0.0412 / math.sqrt(n)) * 4.0 / n)
        a.igual(p["clark_evans_donnelly"], don, f"{etq}: la corrección de Donnelly", 1e-9)
        a.cierto(p["clark_evans_donnelly"] < p["clark_evans"],
                 f"{etq}: corregir el borde BAJA el índice",
                 f"{p['clark_evans']:.5f} -> {p['clark_evans_donnelly']:.5f}")

    # El mapa y las cifras tienen que ser del MISMO patrón. Se recalcula la
    # distancia media al vecino desde los puntos cuantizados: la
    # cuantización a 0..q sobre una ventana unidad mete un error de hasta
    # 1/q por coordenada, así que la tolerancia se deriva de q en vez de
    # inventarse.
    peor, saltados = 0.0, 0
    for k, p in enumerate(pats, start=1):
        mapa = M[f"patron-{k:02d}"]
        q = mapa.get("q", 4096)
        a.igual(mapa["n"], p["n"], f"patrón {k:02d}: el mapa trae los n puntos de la ficha")
        # La longitud de `pts` ANTES de tocarla, y no es paranoia de
        # formato: sin esta guarda, un `pts` desbordado hacía que el
        # cálculo de distancias de abajo pidiera una matriz de terabytes y
        # el auditor MURIERA ahí. Moría con código distinto de cero, así
        # que el arnés lo apuntaba como defecto cazado —pero ninguna de las
        # comprobaciones posteriores llegaba a correr, y el presupuesto de
        # geometría se quedaba sin mirar. Un auditor que se cae no es un
        # auditor que informa.
        bien = a.igual(len(mapa["pts"]), 2 * mapa["n"],
                       f"patrón {k:02d}: el mapa trae dos coordenadas por punto")
        if not bien:
            saltados += 1
            continue
        pts = np.array(mapa["pts"], dtype=float).reshape(-1, 2) / q
        d = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
        np.fill_diagonal(d, np.inf)
        peor = max(peor, abs(d.min(axis=1).mean() - p["nn_media"]))
    tol = 4.0 / 4096
    a.cierto(peor < tol and saltados == 0,
             f"las cifras y el dibujo son del mismo patrón, en los {n_pat}",
             f"peor desvío {peor:.6f} de {tol:.6f}" +
             (f" · {saltados} sin contrastar" if saltados else ""))
    for k in range(1, n_pat + 1):
        audita_geomapa(a, M[f"patron-{k:02d}"], f"patron-{k:02d}")

    # -----------------------------------------------------------------
    a.titulo("El reparto por los tres últimos dígitos")
    v = D["variantes"]
    a.igual(v["base"], 0, "los índices van en base cero, declarado")
    a.igual(len(v["m0"]), n_var, "hay una fila por cada documento posible")
    a.igual(len(v["p0"]), n_var, "y las dos columnas miden lo mismo")
    a.cierto(min(v["m0"]) == 0 and max(v["m0"]) == n_mun - 1,
             "los índices de municipio cubren el catálogo entero",
             f"[{min(v['m0'])}, {max(v['m0'])}]")
    a.cierto(min(v["p0"]) == 0 and max(v["p0"]) == n_pat - 1,
             "y los de patrón también", f"[{min(v['p0'])}, {max(v['p0'])}]")
    pares = list(zip(v["m0"], v["p0"]))
    a.igual(len(set(pares)), n_var,
            "las 1000 parejas (municipio, patrón) son distintas")
    a.igual(len({m for m, _ in pares}), n_mun, "ningún municipio se queda sin repartir")
    a.igual(len({p for _, p in pares}), n_pat, "ningún patrón se queda sin repartir")

    # -----------------------------------------------------------------
    a.titulo("T3: los dos correlogramas, recalculados con libpysal")
    t3 = D["t3"]
    lados = {k: t3[k] for k in ("A", "B")}
    n_est = len(ge)
    temp = ge["t_media_anual"].to_numpy()
    a.cierto(len(lados["A"]) == len(lados["B"]) == t3["bandas"],
             "los dos traen las bandas que se declaran", str(t3["bandas"]))
    a.cierto(lados["A"][0] == lados["B"][0],
             "T3: la primera banda es idéntica en los dos")

    # Cuál es el acumulado se DEDUCE aquí, no se lee: es justo lo que el
    # estudiante tiene que deducir, y comprobar que se puede deducir es
    # comprobar que la tarea tiene respuesta.
    def es_acumulado_de(x, y):
        s, acum = 0.0, []
        for f in x:
            s += f["n_pares"]
            acum.append(s)
        return acum == [f["n_pares"] for f in y]

    b_es_acum = es_acumulado_de(lados["A"], lados["B"])
    a_es_acum = es_acumulado_de(lados["B"], lados["A"])
    a.cierto(b_es_acum != a_es_acum,
             "exactamente uno de los dos es el acumulado del otro",
             f"A acumulado: {a_es_acum} · B acumulado: {b_es_acum}")
    sembrado = "B" if b_es_acum else "A"
    correcto = "A" if b_es_acum else "B"

    for etiqueta, acumulado in ((correcto, False), (sembrado, True)):
        for f in lados[etiqueta]:
            lo = 0.0 if acumulado else f["d1"]
            etq = f"T3/{etiqueta} {f['d1']}-{f['d2']} km"
            xy = np.c_[ge.geometry.x.values, ge.geometry.y.values]
            vec = DistanceBand(xy, threshold=f["d2"] * 1000, binary=True,
                               silence_warnings=True).neighbors
            if lo > 0:
                dentro = DistanceBand(xy, threshold=lo * 1000, binary=True,
                                      silence_warnings=True).neighbors
                vec = {k: sorted(set(vec[k]) - set(dentro[k])) for k in vec}
            a.igual(sum(len(x) for x in vec.values()) / 2, f["n_pares"], f"{etq}: las parejas")
            islas = sum(1 for x in vec.values() if not x)
            a.igual(islas, f["sin_vecinos"], f"{etq}: las estaciones sin vecino")
            w = W(vec, silence_warnings=True)
            w.transform = "r"
            # La conversión de convención: esda cuenta n = todas, spdep con
            # zero.policy cuenta n = las que tienen vecino.
            a.igual(Moran(temp, w, permutations=0).I,
                    f["I"] * n_est / (n_est - islas),
                    f"{etq}: la I de Moran, con la convención de esda", 1e-8)

    # Y que el defectuoso PAREZCA bueno: si se viera roto, T3 no evaluaría
    # nada. Esta no es una comprobación de aritmética, es una del diseño.
    I_mal = [f["I"] for f in lados[sembrado]]
    a.cierto(all(x > y for x, y in zip(I_mal, I_mal[1:])),
             "el correlograma sembrado decae de forma limpia y monótona",
             " ".join(f"{x:.3f}" for x in I_mal))

    # -----------------------------------------------------------------
    a.titulo("T5: grados declarados como metros, rehecho con geopandas")
    t5 = D["t5"]
    fila = gm[gm["shapeName"] == t5["municipio"]]
    a.cierto(len(fila) >= 1, "el municipio del ejemplo existe en adm2", t5["municipio"])
    p = fila.geometry.representative_point().iloc[0]
    d = np.hypot(xy_est[:, 0] - p.x, xy_est[:, 1] - p.y)
    cerca = np.argsort(d, kind="stable")[:t5["n_puntos"]]
    ll = ge.iloc[cerca].to_crs(4326)
    lon = ll.geometry.x.to_numpy()
    lat = ll.geometry.y.to_numpy()

    a.cerca(lon.min(), t5["caja_declarada"][0], "T5: la caja declarada, xmin", 1e-9)
    a.cerca(lat.max(), t5["caja_declarada"][3], "T5: la caja declarada, ymax", 1e-9)
    # La distancia de verdad, sobre el elipsoide, con pyproj y no con s2:
    # otro camino que el de R.
    # LA CONVENCIÓN QUE ESTE AUDITOR DESTAPÓ, y que acabó mejorando T7.
    #
    # `sf::st_distance()` sobre lon/lat NO mide en el elipsoide: mide en la
    # esfera de s2, de radio 6 371 010 m. Contra `pyproj.Geod(WGS84)` la
    # diferencia es del 0.43 % en este par —cien veces la tolerancia—, y no
    # es un error de nadie: son dos Tierras distintas. Así que se comprueba
    # contra la esfera, con una implementación propia del círculo máximo
    # (independiente de s2 y de sf), y ADEMÁS se mide la brecha contra el
    # elipsoide, que es una cifra que el taller ahora publica.
    from pyproj import Geod
    geod = Geod(ellps="WGS84")

    def circulo_maximo(lo1, la1, lo2, la2, radio):
        f1, f2 = math.radians(la1), math.radians(la2)
        dl = math.radians(lo2 - lo1)
        cos_c = math.sin(f1) * math.sin(f2) + math.cos(f1) * math.cos(f2) * math.cos(dl)
        return radio * math.acos(min(1.0, max(-1.0, cos_c)))

    radio_s2 = D["t7"]["radio_esfera_s2_m"]
    a.igual(radio_s2, 6371010.0, "T5/T7: el radio de la esfera de s2, declarado en el JSON", 1e-6)
    d_esfera = circulo_maximo(lon[0], lat[0], lon[1], lat[1], radio_s2)
    a.cerca(d_esfera / 1000, t5["d_real_km"],
            "T5: los km entre las dos primeras, sobre la esfera de s2", 1e-9)
    _, _, d_real = geod.inv(lon[0], lat[0], lon[1], lat[1])
    a.cierto(abs(d_real / 1000 / t5["d_real_km"] - 1) < 0.01,
             "T5: y la geodésica elipsoidal queda cerca, pero NO igual",
             f"{d_real / 1000:.5f} km frente a {t5['d_real_km']:.5f} "
             f"({100 * (d_real / 1000 / t5['d_real_km'] - 1):+.3f} %)")
    # Y la que sale de declarar los grados como metros: euclídea, plana.
    d_mal = math.hypot(lon[0] - lon[1], lat[0] - lat[1])
    a.igual(d_mal, t5["d_declarada_m"], "T5: los «metros» que devuelve la declaración falsa", 1e-9)
    a.cerca(t5["d_real_km"] * 1000 / t5["d_declarada_m"], t5["veces"],
            "T5: el cociente entre las dos medidas", 1e-9)
    a.cierto(t5["veces"] > 1e4, "T5: el disparate es de cuatro órdenes de magnitud o más",
             f"{t5['veces']:.0f} veces")
    dist_al_primero = np.hypot(lon - lon[0], lat - lat[0])
    a.igual(int((dist_al_primero <= 500).sum()), t5["en_buffer_500"],
            "T5: cuántos puntos se traga un buffer de 500 «metros»")
    a.igual(t5["en_buffer_500"], t5["n_puntos"],
            "T5: se los traga TODOS, que es el síntoma que hay que ver")

    # -----------------------------------------------------------------
    a.titulo("T6: la fuga espacial, contra el CSV de Saber 11")
    t6 = D["t6"]
    import pandas as pd
    s11 = pd.read_csv(PROCESADO / "municipios_saber11.csv", dtype={"divipola": str})
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype=str)
    gm2 = gpd.read_file(PROCESADO / "colombia_adm2.gpkg").merge(
        llave[["shapeID", "divipola"]], on="shapeID", how="left").merge(
        s11[["divipola", "s11_punt_medio"]], on="divipola", how="left")
    z = gm2["s11_punt_medio"].dropna().to_numpy()
    a.igual(len(z), t6["n"], "T6: municipios con puntaje, contados por pandas")
    a.cerca(z.std(ddof=1), t6["sd_variable"], "T6: la desviación del puntaje", 1e-8)
    # El R² publicado tiene que salir del RMSE publicado y de una varianza
    # que se calcula AQUÍ, desde el CSV: eso ata las dos cifras a un dato
    # externo en vez de comprobarlas una contra la otra.
    var = z.var(ddof=1)
    for cual in ("aleatoria", "bloques"):
        a.igual(1 - t6[f"rmse_{cual}"] ** 2 / var, t6[f"r2_{cual}"],
                f"T6: el R² por CV {cual} sale de su RMSE", 1e-8)
    a.cierto(t6["rmse_bloques"] > t6["rmse_aleatoria"],
             "T6: la CV por bloques sale PEOR",
             f"{t6['rmse_aleatoria']:.4f} -> {t6['rmse_bloques']:.4f}")
    a.igual(sum(t6["tam_pliegues"]), t6["n"], "T6: los pliegues espaciales suman n")
    a.igual(len(t6["tam_pliegues"]), t6["n_pliegues"], "T6: y son los que se declaran")
    # Lo que NO se puede rehacer aquí, dicho antes de que alguien lo dé por
    # comprobado: el reparto en pliegues sale del RNG de R y de su kmeans.
    # Ninguna de las dos cosas se reproduce desde Python, así que las dos
    # cifras de RMSE se auditan por sus consecuencias —el R², el orden, el
    # reparto— y no rehaciendo la validación cruzada.
    a.salta("los dos RMSE, recalculados por otro camino",
            "los pliegues salen de set.seed() y kmeans() de R, que no se "
            "reproducen desde Python; se auditan por sus consecuencias")

    # -----------------------------------------------------------------
    a.titulo("T7: las cifras que hacen verificable cada afirmación")
    t7 = D["t7"]
    a.igual(t7["n_estaciones"], n_est, "T7: las estaciones son las 361 del capítulo 1")
    # 1e-9: -1/360 es periódico y el JSON lo publica con diez decimales,
    # así que el redondeo deja 2.2e-11 de residuo. A 1e-12 esto fallaba
    # sobre una cifra perfectamente correcta.
    a.igual(t7["moran_esperado"], -1.0 / (n_est - 1), "T7: E[I] = -1/(n-1)", 1e-9)
    todas = ge.to_crs(4326)
    lon_t = todas.geometry.x.to_numpy()
    lat_t = todas.geometry.y.to_numpy()
    a.cerca(lat_t.min(), t7["lat_min"], "T7: la latitud más al sur", 1e-9)
    a.cerca(lat_t.max(), t7["lat_max"], "T7: la más al norte", 1e-9)
    iu = np.triu_indices(n_est, k=1)
    lon1, lon2 = lon_t[iu[0]], lon_t[iu[1]]
    lat1, lat2 = lat_t[iu[0]], lat_t[iu[1]]
    f1, f2 = np.radians(lat1), np.radians(lat2)
    cos_c = (np.sin(f1) * np.sin(f2) +
             np.cos(f1) * np.cos(f2) * np.cos(np.radians(lon2 - lon1)))
    d_esf = radio_s2 * np.arccos(np.clip(cos_c, -1.0, 1.0))    # la esfera de s2
    _, _, d_eli = geod.inv(lon1, lat1, lon2, lat2)             # el elipsoide WGS84
    d_gra = np.hypot(lon1 - lon2, lat1 - lat2) * 111.32 * 1000
    razon = d_gra / d_esf
    a.igual(len(razon), n_est * (n_est - 1) // 2, "T7: las 64 980 parejas de estaciones")
    a.igual(t7["n_parejas"], n_est * (n_est - 1) // 2,
            "T7: y el conteo que publica R es ese mismo")
    a.cerca(100 * (np.median(razon) - 1), t7["error_grados_pct_mediano"],
            "T7: el error mediano de «111.32 km por grado»", 1e-6)
    a.cerca(100 * np.abs(razon - 1).max(), t7["error_grados_pct_max"],
            "T7: y el máximo", 1e-6)
    a.cierto(0 < t7["error_grados_pct_mediano"] < t7["error_grados_pct_max"] < 10,
             "T7: la afirmación a medias lo es de verdad",
             f"{t7['error_grados_pct_mediano']:.2f} % a {t7['error_grados_pct_max']:.2f} %")

    # La brecha esfera/elipsoide, rehecha con pyproj contra la lwgeom de R.
    # Las dos resuelven la geodésica de Karney, pero por enlaces distintos.
    brecha = d_esf / d_eli
    a.cerca(100 * (np.median(brecha) - 1), t7["brecha_esfera_elipsoide_pct_mediana"],
            "T7: la brecha entre la esfera de s2 y el elipsoide", 1e-3)
    a.cerca(100 * np.abs(brecha - 1).max(), t7["brecha_esfera_elipsoide_pct_max"],
            "T7: y su máximo", 1e-3)
    # Y el hallazgo que hace que la afirmación a medias sea buena: medir en
    # otra Tierra desplaza MÁS que medir en grados.
    a.cierto(t7["brecha_esfera_elipsoide_pct_mediana"] > t7["error_grados_pct_mediano"],
             "T7: la brecha que nadie mira es la mayor",
             f"{t7['brecha_esfera_elipsoide_pct_mediana']:.2f} % frente a "
             f"{t7['error_grados_pct_mediano']:.2f} %")
    a.cerca(111.32 * math.cos(math.radians(t7["lat_max"])), t7["km_por_grado_lon_norte"],
            "T7: el grado de longitud en el norte", 1e-9)
    a.cerca(111.32 * math.cos(math.radians(t7["lat_min"])), t7["km_por_grado_lon_sur"],
            "T7: y en el sur", 1e-9)

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
