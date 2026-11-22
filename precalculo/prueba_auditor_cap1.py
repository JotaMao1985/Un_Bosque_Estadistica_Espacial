#!/usr/bin/env python3
"""
prueba_auditor_cap1.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T1.1.

POR QUÉ EXISTE. `audita_cap1.py` informó **818 comprobaciones, 0 fallos**
la primera vez que corrió limpio. Ese número no significa nada por sí
solo: un auditor cuyo silencio no se ha interrogado no es un auditor
verificado. Es la lección que este proyecto ya pagó dos veces —cinco
auditores de DOE que jamás miraron dentro de KaTeX, y dos comprobaciones
de T0.5 que eran **incapaces de fallar** porque buscaban una cadena que
estaba en un comentario del propio archivo—.

CÓMO FUNCIONA. Copia los tres JSON del precálculo, introduce en la copia
un defecto concreto, ejecuta el auditor apuntando a la copia con sus
variables de entorno y comprueba que devuelve código distinto de cero.
**Los archivos publicados no se tocan nunca**, y al final se verifica
byte a byte que siguen igual.

LAS DOS REGLAS DEL ARNÉS, las dos aprendidas a golpes:

  1. **Cada tanda empieza y acaba con un CONTROL sin inyectar nada.** Si
     el auditor no sale limpio sobre el original, cualquier «acierto»
     posterior es falso.
  2. **«25 de 25» no basta.** Se cuenta también cuántas comprobaciones
     DISTINTAS se han visto fallar alguna vez. Una comprobación que
     nunca ha fallado puede estar bien escrita o puede ser incapaz de
     fallar, y desde fuera se ven igual.

LAS FAMILIAS DE DEFECTO. Cada una imita un fallo que ya ocurrió de
verdad en este proyecto:

   1. cifra publicada que deja de cuadrar con la fuente primaria
   2. cifra derivada que deja de cuadrar con las que la generan
   3. relación cualitativa que se rompe (monotonías, órdenes, signos)
   4. control interno del generador desactivado desde fuera
   5. discrepancia R↔Python que deja de estar declarada   ← A.2
   6. discrepancia declarada sin causa explicada          ← A.2
   7. cortes o geometría del .geomapa alterados           ← T0.3
   8. presupuesto de peso desbordado                      ← §4 del plan
   9. tilde convertida en bytes crudos <c3><b3>           ← T0.5
  10. flotante con más decimales de los declarados (doble redondeo) ← T0.5
  11. solución de un ejercicio guiado alterada
  12. coherencia entre módulos rota
  13. metadato o frontera declarada que desaparece

Uso:  python3 precalculo/prueba_auditor_cap1.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import copy
import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_cap1.py"

ARCHIVOS = {
    "datos": ("CAP1_DATOS", "cap1_datos.json"),
    "mapas": ("CAP1_MAPAS", "cap1_mapas.json"),
    "soluciones": ("CAP1_SOLUCIONES", "cap1_soluciones.json"),
}

# El intérprete tiene que ser el de geo_env: el auditor necesita
# geopandas, libpysal y esda. Se lee de versiones_py.json, que lo congeló
# T0.1, en vez de darlo por sabido.
PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


# =====================================================================
# Los defectos. Dos formas: mutar el objeto ya parseado, o sustituir
# texto en el archivo (para lo que no sobrevive a un round-trip de JSON,
# como los bytes crudos o un NaN).
# =====================================================================
def defectos() -> list[tuple[str, str, str, object]]:
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""

    def m(f):          # azúcar para declarar una mutación
        return ("obj", f)

    D: list[tuple[str, str, str, object]] = []

    def add(nombre, archivo, tipo_accion):
        D.append((nombre, archivo, tipo_accion[0], tipo_accion[1]))

    # --- 1. Cifra publicada que deja de cuadrar con la fuente primaria --
    add("el I de Moran municipal cambia", "datos",
        m(lambda o: o["escala"].__setitem__("moran_municipal_n_total", 0.41739)))
    add("la deserción media deja de ser la del GeoPackage", "datos",
        m(lambda o: o["colombia"]["area"].__setitem__("media", 3.71483)))
    add("el gradiente térmico se sale del rango físico", "datos",
        m(lambda o: o["colombia"]["geo"].__setitem__("gradiente", -8.41377)))
    add("las muertes de Snow dejan de ser 578", "datos",
        m(lambda o: o["snow"].__setitem__("n_muertes", 571)))
    add("la tasa de SIDS de nc cambia", "datos",
        m(lambda o: o["area_canonico"].__setitem__("tasa_media", 2.31749)))
    add("una versión de paquete inventada", "datos",
        m(lambda o: o["ecosistema"]["paquetes"][0].__setitem__("version", "1.0.71")))

    # --- 2. Cifra derivada que deja de cuadrar con su origen ------------
    add("la caída del I al agregar deja de cuadrar", "datos",
        m(lambda o: o["escala"].__setitem__("caida_pct", 79.41263)))
    add("el factor del e.e. real deja de cuadrar con sus dos e.e.", "datos",
        m(lambda o: o["inferencia_real"].__setitem__("factor", 3.71429)))
    add("el n efectivo deja de salir del factor", "datos",
        m(lambda o: o["inferencia_real"].__setitem__("n_eff", 81.34917)))
    add("una celda de la rejilla de n_eff mal calculada", "datos",
        m(lambda o: o["n_efectivo"]["rejilla"][3]["n_eff"].__setitem__(4, 71.4913)))
    add("el error de Monte Carlo publicado no es el de su cobertura", "datos",
        m(lambda o: o["inferencia"]["rejilla"][4].__setitem__(
            "emc_cobertura", 0.0141379)))
    add("la inflación de la CV deja de cuadrar con su razón", "datos",
        m(lambda o: o["cv_espacial"].__setitem__("inflacion_pct", 91.41773)))
    # El denominador de Clark-Evans, que el módulo 3 publica al lado del
    # numerador para que el lector pueda hacer la división. Publicada la
    # cuenta, tiene que cuadrar: si `nn_esperada` se moviera sola, la tabla
    # enseñaría una división que no da.
    add("la distancia esperada bajo CSR deja de cuadrar con su índice", "datos",
        m(lambda o: o["puntual_canonico"]["cells"].__setitem__(
            "nn_esperada", 0.0714913)))
    # La corrección de borde, por sus dos lados: que el número no cuadre con
    # la fórmula, y que deje de bajar el índice —que es lo que el módulo 3
    # afirma en prosa sobre los tres patrones a la vez—.
    add("la R corregida por borde deja de cuadrar con Donnelly", "datos",
        m(lambda o: o["puntual_canonico"]["redwood"].__setitem__(
            "clark_evans_donnelly", 0.5714913)))
    add("corregir el borde deja de bajar el índice", "datos",
        m(lambda o: o["puntual_canonico"]["japanesepines"].__setitem__(
            "clark_evans_donnelly", 1.1497134)))

    # --- 3. Relación cualitativa rota -----------------------------------
    add("la cobertura deja de caer al subir phi", "datos",
        m(lambda o: o["inferencia"]["rejilla"][3].__setitem__("cobertura", 0.71349)))
    add("un n_eff supera a n", "datos",
        m(lambda o: o["inferencia"]["rejilla"][2].__setitem__("n_eff", 417.1349)))
    add("la agregación deja de subir la correlación", "datos",
        m(lambda o: o["agregacion"]["niveles"][3].__setitem__("corr", 0.17493)))
    add("Clark-Evans deja de ordenar los tres regímenes", "datos",
        m(lambda o: o["tobler"]["clark_evans"].__setitem__("cells", 0.41397)))
    add("el correlograma permutado deja de estar plano", "datos",
        m(lambda o: o["tobler"]["permutado"]["bandas"][2].__setitem__("I", 0.71483)))
    add("el I de los campos deja de crecer con el rango", "mapas",
        m(lambda o: o["campos"][3].__setitem__("moran", 0.11397)))

    # --- 4. Control interno desactivado desde fuera ----------------------
    add("el bootstrap i.i.d. deja de reproducir el e.e. analítico", "datos",
        m(lambda o: o["inferencia_real"].__setitem__("ee_bootstrap_iid", 0.0714913)))
    add("el e.e. simulado deja de reproducir el exacto", "datos",
        m(lambda o: o["inferencia"]["rejilla"][5].__setitem__("ee_real", 0.4713977)))
    add("la estabilidad ante unidades pequeñas se declara sin serlo", "datos",
        m(lambda o: o["escala_correlacion"]["principal"].__setitem__(
            "diferencia_umbral_30", 0.4137941)))

    # --- 5 y 6. Las discrepancias declaradas (la lección de A.2) --------
    add("la discrepancia del I de Moran desaparece de la lista", "datos",
        m(lambda o: o.__setitem__(
            "discrepancias",
            [d for d in o["discrepancias"] if d["id"] != "moran_islas"])))
    add("una discrepancia se queda sin causa explicada", "datos",
        m(lambda o: o["discrepancias"][2].__setitem__("causa", "cosas de GDAL")))
    add("una discrepancia publica una diferencia que no es la suya", "datos",
        m(lambda o: o["discrepancias"][0].__setitem__("diferencia", 0.0714913)))

    # --- 7. El .geomapa --------------------------------------------------
    add("un corte de clase del mapa de nc cambia", "mapas",
        m(lambda o: o["nc"]["cortes"].__setitem__(2, 1.7149371)))
    add("el n declarado del mapa de Bogotá deja de cuadrar", "mapas",
        m(lambda o: o["bogota"].__setitem__("n", 2183)))
    add("los tamaños de clase dejan de sumar n", "mapas",
        m(lambda o: o["desercion"]["tam"].__setitem__(0, 17)))
    add("un punto se sale de la cuantización", "mapas",
        m(lambda o: o["ideam"]["pts"].__setitem__(4, 41397)))
    add("el mapa de Snow pierde segmentos de calle", "mapas",
        m(lambda o: o.__setitem__(
            "snow", dict(o["snow"], lineas=o["snow"]["lineas"][:391]))))

    # --- 7 bis. El mapa del módulo 7: el resalte (T2.4) ------------------
    #
    # Un resalte torcido es el defecto más silencioso que puede tener este
    # mapa: el lienzo sale igual de bonito señalando el condado de al lado o
    # cinco celdas que el condado no toca. La cadena que lo impide tiene dos
    # eslabones y aquí se rompen los dos por separado —el del cableado, que
    # empareja los dos JSON, y el geométrico, que devuelve los rectángulos
    # dibujados al terreno—, porque un eslabón solo dejaría pasar el caso en
    # que los dos JSON se mueven de acuerdo.
    add("el mapa del módulo 7 resalta el condado vecino", "mapas",
        m(lambda o: o["agregacion"].__setitem__("resaltado", 67)))
    add("el mapa resalta una celda que el condado no toca", "mapas",
        m(lambda o: o["agregacion"]["lineas_resaltadas"].__setitem__(4, 63)))
    add("el mapa pierde una de las celdas resaltadas", "mapas",
        m(lambda o: o["agregacion"].__setitem__(
            "lineas_resaltadas", o["agregacion"]["lineas_resaltadas"][:4])))
    add("el mapa resalta otras cinco celdas, coherentes entre sí", "mapas",
        m(lambda o: o["agregacion"].__setitem__(
            "lineas_resaltadas", [43, 44, 53, 54, 63])))
    add("el precálculo dice que toca otras cinco celdas", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "celdas_tocadas", [43, 44, 53, 54, 63])))
    add("la rejilla del mapa pierde rectángulos", "mapas",
        m(lambda o: o["agregacion"].__setitem__("n_lineas", 96)))
    # Y el caso contrario, que es el silencioso: el array se queda corto y
    # el contador sigue diciendo 100. El mapa dibujaría 96 rectángulos con
    # todo lo demás cuadrando.
    add("el array de rectángulos se queda corto y el contador no se entera", "mapas",
        m(lambda o: o["agregacion"].__setitem__(
            "lineas", o["agregacion"]["lineas"][:96])))

    # --- 7 ter. El caso del módulo 7: sus cifras (T2.4) ------------------
    add("el condado del caso deja de ser el que más infla", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "nombre", "Guilford")))
    add("el índice del condado del caso se desplaza en uno", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "indice", 69)))
    add("las celdas que toca el condado del caso dejan de ser cinco", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "n_celdas_toca", 4)))
    add("lo que aporta el condado por «se tocan» deja de ser k por su conteo", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "aporte_predicado", 176)))
    add("los excesos dejan de sumar la inflación entera", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "exceso_total", 1904)))
    add("una fracción de área del reparto cambia", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"]["reparto"][2]
          .__setitem__("fraccion_pct", 32.4173941)))
    add("el reparto deja de sumar las muertes del condado", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"]["reparto"][0]
          .__setitem__("aporte_area", 17.3941739)))
    add("una celda del reparto cambia de fila", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"]["reparto"][1]
          .__setitem__("fila", 4)))
    add("la celda del roce deja de ser la de menos área", "datos",
        m(lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "roce_pct", 14.1739417)))

    # --- 8. Presupuesto --------------------------------------------------
    add("la geometría se sale del presupuesto de 120 KB", "mapas",
        m(lambda o: o["nc"].__setitem__("relleno", "x" * 70_000)))

    # --- 11. Los ejercicios guiados --------------------------------------
    add("E1: quitar la bomba mueve también a las demás muertes", "soluciones",
        m(lambda o: o["e1"]["solucion"].__setitem__("factor_otras", 1.1739)))
    add("E2: el IC honesto deja de contener al ingenuo", "soluciones",
        m(lambda o: o["e2"]["solucion"].__setitem__("ee_bloques", 0.1739417)))
    # E3 (R1 · T1.2). El ejercicio dejó de «medir» un rho con bandas: el n
    # efectivo sale de dos remuestreos sobre el archivo público y todo lo
    # demás se despeja de él. Los mutantes de los campos del correlograma
    # (`moran_por_banda`, `bandas_km`) se retiraron con los campos.
    e3m = lambda o: o["e3"]["solucion"]       # noqa: E731
    add("E3: el techo deja de ser 1/rho", "soluciones",
        m(lambda o: e3m(o).__setitem__("techo", 41.73914)))
    add("E3: vuelve el rho de las bandas, que no se despeja del n efectivo", "soluciones",
        m(lambda o: e3m(o).__setitem__("rho_medio", 0.0314555721)))
    add("E3: el n efectivo deja de salir de sus dos e.e.", "soluciones",
        m(lambda o: e3m(o).__setitem__("n_eff", 41.7394173)))
    add("E3: el factor deja de ser el cociente de los e.e.", "soluciones",
        m(lambda o: e3m(o).__setitem__("factor", 3.1739417)))
    add("E3: el porcentaje de información deja de ser n_eff/n", "soluciones",
        m(lambda o: e3m(o).__setitem__("pct_informacion", 11.7394173)))
    add("E3: vuelven las 113 estaciones para 25 independientes", "soluciones",
        m(lambda o: e3m(o).__setitem__("n_para_25", 113.3517394)))
    add("E3: las estaciones para 25 se redondean hacia abajo", "soluciones",
        m(lambda o: e3m(o).__setitem__("estaciones_para_25", 56)))
    add("E3: la bandera dice que 50 independientes se alcanzan", "soluciones",
        m(lambda o: e3m(o).__setitem__("objetivo_50_alcanzable", True)))
    add("E3: la temperatura media deja de ser la del archivo público", "soluciones",
        m(lambda o: e3m(o).__setitem__("media", 22.4173941)))
    add("E3: un departamento de más entre los bloques", "soluciones",
        m(lambda o: e3m(o).__setitem__("n_bloques", 33)))
    add("E3: el promedio centrado de todos los pares sale positivo", "soluciones",
        m(lambda o: e3m(o).__setitem__("centrado_todos_los_pares", 0.0027777778)))
    add("E3: con otra semilla el techo pasa de 50", "soluciones",
        m(lambda o: e3m(o)["otras_semillas"].__setitem__("techo_max", 51.7394173)))
    add("E3: el rango de las otras semillas no contiene a la referencia", "soluciones",
        m(lambda o: e3m(o)["otras_semillas"].__setitem__("n_eff_min", 40.9173941)))
    add("E3: el ejercicio vuelve a leer el dato que no se publica", "soluciones",
        m(lambda o: e3m(o).__setitem__(
            "archivo", "datos/procesado/colombia_estaciones_clima.gpkg")))
    add("E3: vuelve el correlograma por bandas al JSON", "soluciones",
        m(lambda o: e3m(o).__setitem__("moran_por_banda", [0.41739, 0.21739])))
    add("E3: la tabla calla sobre el objetivo que no se alcanza", "soluciones",
        m(lambda o: o["e3"].__setitem__(
            "pasos", [p for p in o["e3"]["pasos"] if not isinstance(p["valor"], str)])))

    # Segunda vuelta de T1.2: el jackknife por departamento, los residuos de
    # la altitud y el promedio con pesos por filas.
    jkm = lambda o: e3m(o)["jackknife"]       # noqa: E731
    add("E3: los departamentos del jackknife vuelven al orden de la regional", "soluciones",
        m(lambda o: jkm(o)["por_departamento"].insert(
            0, jkm(o)["por_departamento"].pop(1))))
    add("E3: un departamento cualquiera pasa a llevar el techo sobre 50", "soluciones",
        m(lambda o: jkm(o)["por_departamento"][5].__setitem__("techo", 52.1739417)))
    add("E3: el techo sin un departamento se mueve un 15 %, sin cruzar el umbral", "soluciones",
        m(lambda o: jkm(o)["por_departamento"][7].__setitem__(
            "techo", jkm(o)["por_departamento"][7]["techo"] * 0.85)))
    add("E3: el máximo del jackknife no es el de su lista", "soluciones",
        m(lambda o: jkm(o)["maximo"].__setitem__("techo", 61.7394173)))
    add("E3: el máximo del jackknife cambia de departamento", "soluciones",
        m(lambda o: jkm(o)["maximo"].__setitem__("departamento", "Cundinamarca")))
    add("E3: el mínimo del jackknife cambia de número de estaciones", "soluciones",
        m(lambda o: jkm(o)["minimo"].__setitem__("estaciones", 41)))
    add("E3: dos departamentos voltean la respuesta, según la cuenta", "soluciones",
        m(lambda o: jkm(o).__setitem__("n_sobre_objetivo", 2)))
    add("E3: el jackknife se queda con las réplicas del ejercicio", "soluciones",
        m(lambda o: jkm(o).__setitem__("nboot", 4000)))
    add("E3: la semilla pasa a mover el techo más que el dato", "soluciones",
        m(lambda o: e3m(o)["otras_semillas"].__setitem__("techo_min", 30.1739417)))
    add("E3: la tabla pierde el techo sin el departamento que voltea", "soluciones",
        m(lambda o: o["e3"].__setitem__(
            "pasos", [p for p in o["e3"]["pasos"]
                      if not p["paso"].endswith("sin " + jkm(o)["maximo"]["departamento"])])))
    add("E3: la tabla pierde las estaciones enteras para 25", "soluciones",
        m(lambda o: o["e3"].__setitem__(
            "pasos", [p for p in o["e3"]["pasos"]
                      if p["paso"] != "(b) Estaciones para la precisión de 25"])))
    rsm = lambda o: e3m(o)["residuos"]        # noqa: E731
    add("E3 (d): el R² de la altitud no es el de la regresión", "soluciones",
        m(lambda o: rsm(o).__setitem__("r2", 0.9173941)))
    add("E3 (d): la correlación de los residuos no se despeja de su n efectivo", "soluciones",
        m(lambda o: rsm(o).__setitem__("rho_medio", 0.0156173)))
    add("E3 (d): el techo de los residuos deja de ser 1/rho", "soluciones",
        m(lambda o: rsm(o).__setitem__("techo", 64.1739417)))
    add("E3 (d): la caída de la correlación es «cerca de un tercio» a mano", "soluciones",
        m(lambda o: rsm(o).__setitem__("caida_rho_pct", 31.7394173)))
    add("E3 (d): las estaciones para 50 se redondean hacia abajo", "soluciones",
        m(lambda o: rsm(o).__setitem__("estaciones_para_50",
                                       rsm(o)["estaciones_para_50"] - 1)))
    add("E3 (d): la bandera dice que 50 sigue sin alcanzarse", "soluciones",
        m(lambda o: rsm(o).__setitem__("objetivo_50_alcanzable", False)))
    add("E3 (d): el n para 25 con los residuos no sale de la fórmula", "soluciones",
        m(lambda o: rsm(o).__setitem__("n_para_25", 41.7394173)))
    add("E3 (d): con otra semilla el techo de los residuos baja de 50", "soluciones",
        m(lambda o: e3m(o)["otras_semillas"].__setitem__("residuos_techo_min", 49.1739417)))

    # Como arriba: el mutante que las identidades no ven, ahora en (d).
    def e3_residuos_coherente(o, factor):
        e, r = o["e3"]["solucion"], o["e3"]["solucion"]["residuos"]
        r["ee_bloques"] *= factor
        r["n_eff"] = e["n"] * (r["ee_iid"] / r["ee_bloques"]) ** 2
        rho = (e["n"] / r["n_eff"] - 1) / (e["n"] - 1)
        rho0 = (e["n"] / e["n_eff"] - 1) / (e["n"] - 1)
        r["rho_medio"], r["techo"] = rho, 1 / rho
        r["caida_rho_pct"] = 100 * (1 - rho / rho0)
        b, al = e["objetivos"]
        r["n_para_25"] = b * (1 - rho) / (1 - b * rho)
        r["n_para_50"] = al * (1 - rho) / (1 - al * rho)
        r["estaciones_para_50"] = math.ceil(r["n_para_50"])
        for p in o["e3"]["pasos"]:
            if p["paso"] == f"(d) Estaciones para la precisión de {al}":
                p["valor"] = r["estaciones_para_50"]
    add("E3 (d): el e.e. por departamentos de los residuos baja un 15 %, con todo coherente",
        "soluciones", m(lambda o: e3_residuos_coherente(o, 0.85)))

    pfm = lambda o: e3m(o)["pesos_filas"]     # noqa: E731
    add("E3 (c): el promedio con pesos por filas es el del verificador, no el de estas bandas",
        "soluciones", m(lambda o: pfm(o)["promedio"].__setitem__(1, 0.0191739)))
    add("E3 (c): el promedio con pesos por filas sale negativo", "soluciones",
        m(lambda o: pfm(o)["promedio"].__setitem__(0, -0.0027777778)))
    add("E3 (c): las bandas cambian de ancho sin cambiar la cifra", "soluciones",
        m(lambda o: pfm(o)["anchos_km"].__setitem__(2, 300)))

    # El mutante que las identidades NO ven: el e.e. por departamentos sale
    # un 9 % más bajo y TODO lo que se despeja de él se recalcula coherente,
    # banderas incluidas. Solo lo caza el remuestreo propio del auditor, y
    # está aquí para probar que su tolerancia de Monte Carlo no es un coladero.
    def e3_coherente(o, ee_blq):
        e = o["e3"]["solucion"]
        e["ee_bloques"] = ee_blq
        e["factor"] = ee_blq / e["ee_iid"]
        e["n_eff"] = e["n"] * (e["ee_iid"] / ee_blq) ** 2
        e["pct_informacion"] = 100 * e["n_eff"] / e["n"]
        rho = (e["n"] / e["n_eff"] - 1) / (e["n"] - 1)
        e["rho_medio"], e["techo"] = rho, 1 / rho
        b, al = e["objetivos"]
        e["n_para_25"] = b * (1 - rho) / (1 - b * rho)
        e["estaciones_para_25"] = math.ceil(e["n_para_25"])
        e["objetivo_25_alcanzable"] = b * rho < 1
        e["objetivo_50_alcanzable"] = al * rho < 1
    add("E3: el e.e. por departamentos baja un 9 %, con todo lo derivado coherente",
        "soluciones", m(lambda o: e3_coherente(o, 0.8)))
    # --- R1 · T1.6 (2026-11-16): un mutante por campo nuevo ---------------
    #
    # Los campos que entraron con las imprecisiones del capítulo: la z de las
    # dos I (módulo 7), el alfa de la prueba (módulo 6), la E[I] de cada banda
    # (módulo 3) y, en el módulo 4, dónde caen las réplicas del remuestreo,
    # cuánto mueve la semilla y cuánto mueve quitar un departamento. Más las
    # medias de las réplicas del ejercicio 2. Los «coherentes» mueven una
    # cifra de Monte Carlo y TODO lo que se deriva de ella: solo los caza el
    # remuestreo propio del auditor, y están para probar que su tolerancia no
    # es un coladero.
    esc_ = lambda o: o["escala"]                                     # noqa: E731
    irm = lambda o: o["inferencia_real"]                             # noqa: E731
    rpm = lambda o: irm(o)["replicas"]                               # noqa: E731
    osm_ = lambda o: irm(o)["otras_semillas"]                        # noqa: E731
    sum_ = lambda o: irm(o)["sin_un_departamento"]                   # noqa: E731
    for campo, valor in (("z_municipal", 19.41739), ("z_departamental", 1.71349),
                         ("ee_municipal", 0.0214913), ("ee_departamental", 0.0914137),
                         ("razon_ee", 5.41739)):
        add(f"T1.6 · módulo 7: escala.{campo} deja de cuadrar", "datos",
            m(lambda o, c=campo, v=valor: esc_(o).__setitem__(c, v)))
    add("T1.6 · módulo 6: el alfa de la prueba no es el del t crítico", "datos",
        m(lambda o: o["inferencia"].__setitem__("alfa", 0.01)))
    for campo, valor in (("media_iid", 3.4291473), ("media_bloques", 3.4114937),
                         ("desvio_iid", 0.0041739), ("desvio_bloques", 0.0291473),
                         ("emc_media_iid", 0.0041739), ("emc_media_bloques", 0.0014937),
                         ("esperanza_bloques", 3.4514937), ("desvio_esperanza", 0.0291473),
                         ("emc_esperanza", 0.0014937), ("desvio_esperanza_pct_ee", 3.1417393),
                         ("nrep_esperanza", 4000),
                         ("bloque_min", 5), ("bloque_max", 90)):
        add(f"T1.6 · módulo 4: replicas.{campo} deja de cuadrar", "datos",
            m(lambda o, c=campo, v=valor: rpm(o).__setitem__(c, v)))

    def replicas_coherentes(o, media_blq):
        ir_, r_ = irm(o), rpm(o)
        r_["esperanza_bloques"] = media_blq
        r_["desvio_esperanza"] = media_blq - ir_["media"]
        r_["desvio_esperanza_pct_ee"] = 100 * r_["desvio_esperanza"] / ir_["ee_bootstrap_bloques"]
    add("T1.6 · módulo 4: la esperanza de las réplicas pasa a quedar por debajo, con todo coherente",
        "datos", m(lambda o: replicas_coherentes(o, 3.4)))
    for campo, valor in (("n", 3), ("factor_min", 3.9141739), ("factor_max", 4.5141739),
                         ("factor_sd", 0.9141739), ("n_eff_min", 55.141739),
                         ("n_eff_max", 71.141739)):
        add(f"T1.6 · módulo 4: otras_semillas.{campo} deja de cuadrar", "datos",
            m(lambda o, c=campo, v=valor: osm_(o).__setitem__(c, v)))

    def semillas_coherentes(o, f_min, f_max):
        s_, n_ = osm_(o), irm(o)["n_municipios"]
        s_["factor_min"], s_["factor_max"] = f_min, f_max
        s_["n_eff_min"], s_["n_eff_max"] = n_ / f_max ** 2, n_ / f_min ** 2
    add("T1.6 · módulo 4: el rango de las semillas se corre entero, con todo coherente",
        "datos", m(lambda o: semillas_coherentes(o, 4.5, 4.6)))
    add("T1.6 · módulo 4: el jackknife se queda con las réplicas del módulo", "datos",
        m(lambda o: sum_(o).__setitem__("nboot", 4000)))
    add("T1.6 · módulo 4: los dos remuestreos del jackknife comparten semilla", "datos",
        m(lambda o: sum_(o).__setitem__("semilla_bloques", sum_(o)["semilla_iid"])))
    add("T1.6 · módulo 4: tras quitar un departamento siguen quedando todos", "datos",
        m(lambda o: sum_(o).__setitem__("n_departamentos_quedan", 33)))
    for campo, valor in (("dpto", "99"), ("departamento", "Macondo"), ("municipios", 71),
                         ("factor", 4.9141739), ("n_eff", 81.141739)):
        add(f"T1.6 · módulo 4: una fila del jackknife cambia de {campo}", "datos",
            m(lambda o, c=campo, v=valor: sum_(o)["por_departamento"][3].__setitem__(c, v)))

    def fila_coherente(o, k, factor):
        f, n_ = sum_(o)["por_departamento"][k], irm(o)["n_municipios"]
        f["factor"], f["n_eff"] = factor, (n_ - f["municipios"]) / factor ** 2
    add("T1.6 · módulo 4: el factor sin un departamento sube un 13 %, con su n efectivo coherente",
        "datos", m(lambda o: fila_coherente(o, 3, 4.75)))
    for campo, valor in (("factor_min", 3.4141739), ("factor_max", 4.6141739),
                         ("n_eff_min", 49.141739), ("n_eff_max", 79.141739),
                         ("factor_todos", 4.6141739), ("n_eff_todos", 71.141739),
                         ("ee_jackknife_factor", 0.4141739), ("ee_jackknife_n_eff", 12.141739),
                         ("ee_jackknife_n_eff_pct", 21.41739)):
        add(f"T1.6 · módulo 4: sin_un_departamento.{campo} deja de cuadrar", "datos",
            m(lambda o, c=campo, v=valor: sum_(o).__setitem__(c, v)))
    add("T1.6 · módulo 4: el extremo del jackknife pasa a ser otro departamento", "datos",
        m(lambda o: sum_(o).__setitem__("extremo", dict(sum_(o)["por_departamento"][0]))))
    add("T1.6 · módulo 7: la z de una I departamental igual a la municipal deja de cuadrar", "datos",
        m(lambda o: esc_(o).__setitem__("z_departamental_si_igual", 5.41739)))
    add("T1.6 · módulo 3: la esperanza que imprime el programa no es la de su n", "datos",
        m(lambda o: o["tobler"]["ideam"]["bandas"][1].__setitem__("esperado_programa", -0.0025141)))
    add("T1.6 · módulo 3: las permutaciones de R pasan a dar la convención del programa", "datos",
        m(lambda o: o["tobler"]["permutacion_banda1"].__setitem__(
            "media", o["tobler"]["ideam"]["bandas"][0]["esperado_programa"])))
    add("T1.6 · módulo 3: el error de las permutaciones no es el de su número", "datos",
        m(lambda o: o["tobler"]["permutacion_banda1"].__setitem__("emc", 0.0001141)))
    add("T1.6 · módulo 3: R permuta demasiado poco", "datos",
        m(lambda o: o["tobler"]["permutacion_banda1"].__setitem__("nperm", 500)))
    add("T1.6 · E3: el e.e. jackknife del techo no sale de su lista", "soluciones",
        m(lambda o: o["e3"]["solucion"]["jackknife"].__setitem__("ee_techo", 7.141739)))
    add("T1.6 · módulo 3: en la primera banda todas las estaciones tienen vecinos", "datos",
        m(lambda o: o["tobler"]["ideam"]["bandas"][0].__setitem__("n_con_vecinos", 361)))
    add("T1.6 · módulo 3: la E[I] de la primera banda vuelve a ser la del conjunto", "datos",
        m(lambda o: o["tobler"]["ideam"]["bandas"][0].__setitem__(
            "esperado", o["tobler"]["ideam"]["esperado"])))
    add("T1.6 · módulo 3: una banda de meuse cuenta mal sus puntos con vecinos", "datos",
        m(lambda o: o["tobler"]["meuse"]["bandas"][1].__setitem__("n_con_vecinos", 141)))
    add("T1.6 · módulo 3: la E[I] de una banda del permutado no es la de su n", "datos",
        m(lambda o: o["tobler"]["permutado"]["bandas"][2].__setitem__("esperado", -0.0041739)))
    e2m = lambda o: o["e2"]["solucion"]                              # noqa: E731
    for campo, valor in (("media_replicas_iid", 81.2141739), ("media_replicas_bloques", 80.7141739),
                         ("desvio_replicas_bloques", 0.0414173), ("emc_media_bloques", 0.0414173),
                         ("esperanza_replicas_bloques", 81.2141739), ("desvio_esperanza", 0.0414173),
                         ("emc_esperanza", 0.0091417), ("nrep_esperanza", 4000)):
        add(f"T1.6 · E2: {campo} deja de cuadrar", "soluciones",
            m(lambda o, c=campo, v=valor: e2m(o).__setitem__(c, v)))

    def e2_coherente(o, media_blq):
        e = e2m(o)
        e["media_replicas_bloques"] = media_blq
        e["desvio_replicas_bloques"] = media_blq - e["media"]
    add("T1.6 · E2: las réplicas por bloques se corren 0.3 puntos, con su desvío coherente",
        "soluciones", m(lambda o: e2_coherente(o, 81.3185191793)))
    def e2_esperanza_coherente(o, desvio):
        e = e2m(o)
        e["desvio_esperanza"] = desvio
        e["esperanza_replicas_bloques"] = e["media"] + desvio
    add("T1.6 · E2: la esperanza de las réplicas cambia de lado, con su desvío coherente",
        "soluciones", m(lambda o: e2_esperanza_coherente(o, 0.02)))
    add("T1.6 · E2: un intervalo deja de estar centrado en la media de los municipios", "soluciones",
        m(lambda o: e2m(o)["ic_bloques"].__setitem__(1, e2m(o)["ic_bloques"][1] + 0.4)))
    add("E4: la r deja de crecer con el tamaño de la unidad", "soluciones",
        m(lambda o: o["e4"]["solucion"]["conglomerado"].__setitem__("r", 0.41739)))
    add("E4: la r municipal deja de ser la del módulo 7", "soluciones",
        m(lambda o: o["e4"]["solucion"]["municipal"].__setitem__("r", 0.4173941)))

    # --- El recuadro de los 13 pares y su caso de aviso (2026-09-24) -------
    # El módulo 7 publicaba «8 suben, 5 bajan y 1 invierte» —suma 14— y
    # usaba como prueba la inversión que el generador guardaba como aviso.
    # Cada pieza de la corrección tiene que poder fallar.
    EC = lambda o: o["escala_correlacion"]
    AV = lambda o: o["escala_correlacion"]["caso_aviso"]
    add("una r departamental de los 13 pares cambia", "datos",
        m(lambda o: EC(o)["pares"][5].__setitem__("r_departamental", 0.4137294)))
    add("suben y bajan se reparten distinto, sumando 13", "datos",
        m(lambda o: (EC(o).__setitem__("n_suben", 7), EC(o).__setitem__("n_bajan", 6))))
    add("el que cambia de signo sale de los que bajan", "datos",
        m(lambda o: EC(o).__setitem__("n_invierten_entre_bajan", 0)))
    add("la p del aviso cae por debajo de 0.05", "datos",
        m(lambda o: AV(o).__setitem__("p_departamental", 0.0417394)))
    add("la cobertura del estrato vuelve a la cifra de T0.4", "datos",
        m(lambda o: AV(o).__setitem__("cor_cobertura_puntaje", 0.5952)))
    add("un municipio más con el estrato poco declarado", "datos",
        m(lambda o: AV(o).__setitem__("n_bajo_umbral", 14)))
    add("el aviso sin esos municipios deja de estar en cero", "datos",
        m(lambda o: AV(o).__setitem__("r_departamental_sin_bajo_umbral", -0.1714937)))
    add("el aviso con n >= 30 deja de estar en cero", "datos",
        m(lambda o: AV(o).__setitem__("r_departamental_n30", -0.1714937)))
    add("el recorrido de quitar un municipio se estrecha", "datos",
        m(lambda o: AV(o).__setitem__("loo_min", -0.3714937)))
    add("el municipio que más mueve la r es otro", "datos",
        m(lambda o: AV(o)["influyente"].__setitem__("municipio", "Inírida")))
    add("la r sin ese municipio cambia", "datos",
        m(lambda o: AV(o)["influyente"].__setitem__("r_departamental_sin_el", -0.0417394)))
    add("sin ese municipio su departamento sigue primero", "datos",
        m(lambda o: AV(o)["influyente"].__setitem__("puesto_sin", 1)))
    add("el departamento segundo en estrato es otro", "datos",
        m(lambda o: AV(o)["influyente"].__setitem__("segundo", "Antioquia")))
    add("un par sin estrato deja de bajar con n >= 30", "datos",
        m(lambda o: AV(o)["bajan_sin_estrato"][1].__setitem__("r_departamental_n30", 0.6137294)))
    add("la tesis se apoya en un par sin estrato menos", "datos",
        m(lambda o: AV(o)["bajan_sin_estrato"].pop()))

    # --- 12. Coherencia entre módulos ------------------------------------
    add("los módulos 4 y 6 dejan de medir lo mismo", "datos",
        m(lambda o: o["una_realizacion"].__setitem__("pct_rechaza_ingenuo", 41.7394)))
    add("el n_eff del módulo 5 deja de ser el del módulo 4", "datos",
        m(lambda o: o["n_efectivo"].__setitem__("desercion_municipal", 91.7394)))
    add("el variograma teórico deja de ser el del proceso", "datos",
        m(lambda o: o["una_realizacion"]["variograma"]["teorico"].__setitem__(
            2, 0.9173941)))

    # --- 13. Metadatos y fronteras ---------------------------------------
    add("la frontera con el capítulo 10 desaparece", "datos",
        m(lambda o: o["cv_espacial"].__setitem__(
            "frontera", "se verá más adelante en el curso")))
    add("una fila del glosario pierde una columna", "datos",
        m(lambda o: o["glosario"]["filas"][4].__setitem__("en_r", "")))
    add("dos filas del glosario comparten símbolo", "datos",
        m(lambda o: o["glosario"]["filas"][3].__setitem__(
            "simbolo", o["glosario"]["filas"][2]["simbolo"])))
    add("una hoja del árbol se queda sin capítulo", "datos",
        m(lambda o: o["arbol"]["nodos"][1]["opciones"][0].pop("capitulo")))
    add("el generador dice haber verificado menos anclas", "datos",
        m(lambda o: o["meta"].__setitem__("anclas_verificadas", 3)))
    add("las soluciones cambian de semilla", "soluciones",
        m(lambda o: o["meta"].__setitem__("semilla", 1997)))
    add("los pliegues de la CV dejan de sumar n", "datos",
        m(lambda o: o["cv_espacial"]["tam_pliegues"].__setitem__(0, 17)))

    # --- 14. La curva de un simulador deja de ser la de su mapa ----------
    #
    # T1.3, y la familia nace de un defecto que estuvo publicado: el botón
    # del módulo 6 cambiaba el mapa y la curva del variograma se quedaba
    # quieta, dibujando siempre un campo que **no era ninguno de los tres
    # mapas** —eran dos simulaciones distintas, de rejilla y semilla
    # distintas, emparejadas por el índice—. Ninguna comprobación de las
    # trece familias anteriores podía verlo: cada JSON era correcto por su
    # cuenta y el defecto vivía en el hueco entre los dos.
    #
    # Por eso estas inyecciones atacan por los dos lados: cambiando la curva
    # publicada (y el mapa se queda como estaba) y cambiando el campo del
    # mapa (y la curva se queda como estaba). Una comprobación que solo
    # mirase uno de los dos archivos pasaría la mitad de ellas.
    add("la curva de una realización es la de otra", "datos",
        m(lambda o: o["realizaciones_vistas"][0].__setitem__(
            "variograma", list(o["realizaciones_vistas"][1]["variograma"]))))
    add("un rezago de un variograma se desvía de su campo", "datos",
        m(lambda o: o["realizaciones_vistas"][2]["variograma"].__setitem__(
            5, o["realizaciones_vistas"][2]["variograma"][5] + 0.02)))
    add("las tres curvas se vuelven la misma", "datos",
        m(lambda o: [r.__setitem__("variograma",
                                   list(o["realizaciones_vistas"][0]["variograma"]))
                     for r in o["realizaciones_vistas"]]))
    add("la media de una realización deja de ser la de su campo", "datos",
        m(lambda o: o["realizaciones_vistas"][1].__setitem__("media", 0.4173941)))
    add("la sd de una realización deja de ser la de su campo", "datos",
        m(lambda o: o["realizaciones_vistas"][0].__setitem__("sd", 0.9173941)))
    add("el módulo 6 publica una rejilla que no es la de sus mapas", "datos",
        m(lambda o: o["una_realizacion"].__setitem__("k", 28)))
    add("el desvío máximo publicado no es el de su curva", "datos",
        m(lambda o: o["realizaciones_vistas"][1].__setitem__(
            "desvio_rel_max", 0.4173941)))
    add("el rezago del desvío máximo señala a otro", "datos",
        m(lambda o: o["realizaciones_vistas"][2].__setitem__("lag_desvio_max", 2)))
    # R1 · T1.4: la referencia del variograma es el teórico PROMEDIADO EN LA
    # CLASE. Un mutante por campo nuevo o cambiado.
    add("el teórico de una clase no es el promedio sobre sus pares", "datos",
        m(lambda o: o["una_realizacion"]["variograma"]["teorico_clase"].__setitem__(
            0, o["una_realizacion"]["variograma"]["teorico"][0])))
    add("el número de pares de una clase no es el de la retícula", "datos",
        m(lambda o: o["una_realizacion"]["variograma"]["n_pares"].__setitem__(1, 1289)))
    add("la media de las réplicas se va del teórico de la clase", "datos",
        m(lambda o: o["una_realizacion"]["variograma"]["media"].__setitem__(
            0, o["una_realizacion"]["variograma"]["teorico"][0])))
    add("el ancho de banda del rezago 4 vuelve a medirse contra gamma(4)", "datos",
        m(lambda o: o["una_realizacion"].__setitem__(
            "banda_rel_lag4",
            (o["una_realizacion"]["variograma"]["q95"][3]
             - o["una_realizacion"]["variograma"]["q05"][3])
            / o["una_realizacion"]["variograma"]["teorico"][3])))
    add("el desvío del rezago 4 vuelve a medirse contra gamma(4)", "datos",
        m(lambda o: o["realizaciones_vistas"][0].__setitem__(
            "desvio_rel_lag4",
            abs(o["realizaciones_vistas"][0]["variograma"][3]
                - o["una_realizacion"]["variograma"]["teorico"][3])
            / o["una_realizacion"]["variograma"]["teorico"][3])))
    add("el desvío máximo vuelve a medirse contra gamma en h entero", "datos",
        m(lambda o: o["realizaciones_vistas"][1].__setitem__(
            "desvio_rel_max",
            max(abs(v - t) / t for v, t in zip(
                o["realizaciones_vistas"][1]["variograma"],
                o["una_realizacion"]["variograma"]["teorico"])))))
    # R1 · T1.4: la referencia de Thiessen con puntos uniformes (módulo 10).
    RU = lambda o: o["diseno_modelo"]["referencia_uniforme"]
    add("la referencia uniforme desaparece", "datos",
        m(lambda o: o["diseno_modelo"].pop("referencia_uniforme")))
    add("la referencia uniforme no usa tantos puntos como estaciones", "datos",
        m(lambda o: RU(o).__setitem__("n_puntos", 360)))
    add("la referencia uniforme se queda en treinta muestras", "datos",
        m(lambda o: RU(o).__setitem__("n_muestras", 30)))
    add("la mediana de la referencia es la de otra distribución", "datos",
        m(lambda o: RU(o).__setitem__("razon_mediana", 51.73941)))
    add("el percentil 5 de la referencia no es el suyo", "datos",
        m(lambda o: RU(o).__setitem__("razon_p05", 27.17394)))
    add("el percentil 95 de la referencia no es el suyo", "datos",
        m(lambda o: RU(o).__setitem__("razon_p95", 81.73941)))
    add("el IC de la mediana deja fuera a la mediana", "datos",
        m(lambda o: RU(o).__setitem__(
            "razon_mediana_ic95", [RU(o)["razon_mediana"] + 0.5, RU(o)["razon_mediana"] + 3])))
    add("el IC de la mediana es diez veces más ancho", "datos",
        m(lambda o: RU(o).__setitem__(
            "razon_mediana_ic95", [RU(o)["razon_mediana"] - 15, RU(o)["razon_mediana"] + 15])))
    add("el máximo de la referencia es una razón corriente", "datos",
        m(lambda o: RU(o).__setitem__("razon_max", RU(o)["razon_p95"] + 1)))
    add("«veces la mediana» no es el cociente", "datos",
        m(lambda o: RU(o).__setitem__("red_sobre_mediana", 41.73941)))
    add("«veces el percentil 95» no es el cociente", "datos",
        m(lambda o: RU(o).__setitem__("red_sobre_p95", 17.39412)))
    add("los rezagos fuera de banda declarados no son los que hay", "datos",
        m(lambda o: o["realizaciones_vistas"][0].__setitem__("lags_fuera_banda", 3)))
    add("el campo del mapa cambia y su curva no", "mapas",
        m(lambda o: o["realizaciones"][1]["zq"].__setitem__(
            slice(0, 64), [0] * 64)))
    add("el mapa de una realización lleva el id de otra", "mapas",
        m(lambda o: o["realizaciones"][2].__setitem__("id", 1)))
    add("un mapa del módulo 6 vuelve a la rejilla de 28×28", "mapas",
        m(lambda o: o["realizaciones"][0].__setitem__("nx", 28)))
    # Las dos de abajo no buscan una cifra falsa sino una AUSENCIA, y están
    # porque las dos primeras versiones de estas comprobaciones no informaban
    # de ellas: se estrellaban. El código de salida era 1 igual y el arnés las
    # daba por cazadas, pero un auditor que revienta deja de contar las 900
    # comprobaciones restantes. Cazar no es fallar: es fallar diciendo qué.
    add("una fila del módulo 6 pierde su variograma", "datos",
        m(lambda o: o["realizaciones_vistas"][2].pop("variograma")))
    add("un mapa del módulo 6 pierde celdas", "mapas",
        m(lambda o: o["realizaciones"][1].__setitem__(
            "zq", o["realizaciones"][1]["zq"][:200])))

    # --- 15. El módulo 5 sobre lo verdadero (R1) --------------------------
    #
    # Hasta R1 esta tanda atacaba un rho DESPEJADO y un rho «MEDIDO» por
    # bandas, y la distancia entre los dos. El segundo se retiró: el promedio
    # centrado de todos los pares vale -1/(n-1) con cualquier dato, así que no
    # medía la correlación media. Lo que el módulo publica ahora son tres
    # cosas, y las inyecciones atacan las tres: que la fórmula con el rho
    # medio ES el n_eff exacto, que el promedio centrado es -1/(n-1) y no
    # depende del dato, y que el techo 1/rho solo aparece al rellenar.
    add("el rho medio del titular deja de ser el despeje", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "implicito", 0.0173941)))
    add("vuelve un «rho medido» sobre el mapa al titular", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "estimado", 0.0021195)))
    add("el rho medio de un campo no es el de la retícula", "datos",
        m(lambda o: o["n_efectivo"]["exacto_campo"][4].__setitem__(
            "rho_medio", 0.2173941)))
    add("el n_eff de la fórmula se separa del exacto", "datos",
        m(lambda o: o["n_efectivo"]["exacto_campo"][4].__setitem__(
            "n_eff_formula", 5.4173941)))
    add("el n_eff exacto de un campo no es el del módulo 4", "datos",
        m(lambda o: o["n_efectivo"]["exacto_campo"][2].__setitem__(
            "n_eff", 41.7394173)))
    add("la fórmula declarada vuelve a hablar de un rho a secas", "datos",
        m(lambda o: o["n_efectivo"].__setitem__(
            "formula", "n_eff = n / (1 + (n-1) rho)")))
    add("el rho medio verdadero de la demostración cambia", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__(
            "rho_medio_verdadero", 0.1739417)))
    add("-1/(n-1) se calcula con n en vez de n-1", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__(
            "menos_inv_n1", -0.00390625)))
    add("el promedio centrado de alguna réplica no es -1/(n-1)", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__(
            "centrado_max", 0.0021195)))
    add("el menor promedio centrado se aparta de -1/(n-1)", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__(
            "centrado_min", -0.0417394)))
    add("la desviación máxima deja de ser redondeo", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__(
            "desviacion_max", 0.0041739)))
    add("con la media verdadera el promedio no apunta al rho medio", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["con_media_verdadera"].__setitem__(
            "media", 0.0417394)))
    add("la dispersión entre réplicas se encoge por debajo del rho medio", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["con_media_verdadera"].__setitem__(
            "sd", 0.0417394)))
    add("el error de Monte Carlo no es sd/sqrt(réplicas)", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["con_media_verdadera"].__setitem__(
            "emc", 0.0173941)))
    add("el porcentaje de réplicas negativas no es el que sale", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["con_media_verdadera"].__setitem__(
            "pct_negativas", 41.7394173)))
    add("la demostración deja de correr sobre las réplicas del módulo 4", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__("nrep", 417)))
    add("el promedio centrado de la deserción no es -1/(n-1)", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["colombia"].__setitem__(
            "centrado", 0.0021195)))
    add("-1/(n-1) de los municipios se calcula con n", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["colombia"].__setitem__(
            "menos_inv_n1", -0.0008920607)))
    add("la demostración habla de otros municipios", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["colombia"].__setitem__("n", 1113)))
    add("un rho medio del relleno no es el de su retícula", "datos",
        m(lambda o: o["n_efectivo"]["techo"]["rejilla"][3]["relleno"].__setitem__(
            "rho_medio", 0.1739417)))
    add("un n_eff del relleno no sale de su rho medio", "datos",
        m(lambda o: o["n_efectivo"]["techo"]["rejilla"][2]["relleno"].__setitem__(
            "n_eff", 5.4173941)))
    # El relleno deja de ESTANCARSE: la última fila se escapa, con su rho
    # medio movido a juego para que la cuenta de la fila siga cuadrando y lo
    # único roto sea el estancamiento.
    add("el relleno deja de estancarse en la última fila", "datos",
        m(lambda o: (
            o["n_efectivo"]["techo"]["rejilla"][3]["relleno"].__setitem__("n_eff", 6.5),
            o["n_efectivo"]["techo"]["rejilla"][3]["relleno"].__setitem__(
                "rho_medio", (4096 / 6.5 - 1) / 4095))))
    add("rho_inf no es la correlación media de la región", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("rho_inf", 0.1941739)))
    add("rho_inf se mueve en la cuarta cifra", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("rho_inf", 0.1936662)))
    add("el techo del relleno no es 1/rho_inf", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("techo_inf", 5.4173941)))
    add("el último salto del relleno no es el de la tabla", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("ultimo_salto_pct", 0.1739417)))
    add("lo que falta para el techo no es lo que falta", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("falta_techo_pct", 0.0417394)))
    add("la región del relleno deja de ser la del módulo 4", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("lado_relleno", 15)))
    add("la ampliación cambia de paso", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("paso_ampliacion", 2)))
    add("el rho medio de Colombia corregido por s² no es su despeje", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "implicito_con_s2", 0.0141739)))
    add("la rebaja por s² no es la que separa los dos rho", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "diferencia_s2_pct", 4.1739417)))
    add("la media del proceso simulado deja de ser 0", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__("media", 0.5)))
    add("la varianza del proceso simulado no es la del módulo 4", "datos",
        m(lambda o: o["n_efectivo"]["centrado"].__setitem__("varianza", 2)))
    add("el porcentaje de réplicas negativas se va a 13", "datos",
        m(lambda o: o["n_efectivo"]["centrado"]["con_media_verdadera"].__setitem__(
            "pct_negativas", 13.0)))
    add("la respuesta del quiz no es la de la rejilla", "datos",
        m(lambda o: o["n_efectivo"]["caso_quiz"].__setitem__("n_eff", 9.4173941)))
    add("el quiz redondea mal su respuesta", "datos",
        m(lambda o: o["n_efectivo"]["caso_quiz"].__setitem__("n_eff_redondo", 9)))
    add("el techo que cita el quiz no es 1/rho", "datos",
        m(lambda o: o["n_efectivo"]["caso_quiz"].__setitem__("techo", 100)))
    add("el distractor del quiz coincide con otra opción", "datos",
        m(lambda o: o["n_efectivo"]["caso_quiz"].__setitem__("ingenuo", 100)))
    add("el otro techo del quiz no es el de su rho", "datos",
        m(lambda o: o["n_efectivo"]["caso_quiz"].__setitem__("techo_otro", 50)))
    add("el quiz pregunta por un n que no está en la rejilla", "datos",
        m(lambda o: o["n_efectivo"]["caso_quiz"].__setitem__("n", 2000)))
    add("un rho medio de la ampliación no es el de su retícula", "datos",
        m(lambda o: o["n_efectivo"]["techo"]["rejilla"][0]["ampliacion"].__setitem__(
            "rho_medio", 0.4173941)))
    add("un n_eff de la ampliación no sale de su rho medio", "datos",
        m(lambda o: o["n_efectivo"]["techo"]["rejilla"][2]["ampliacion"].__setitem__(
            "n_eff", 17.3941739)))
    add("la fila de 16 por lado deja de ser la retícula del módulo 4", "datos",
        m(lambda o: o["n_efectivo"]["techo"]["rejilla"][1].__setitem__("k", 17)))
    add("el factor del relleno no es el cociente de sus extremos", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__(
            "factor_relleno", 1.4173941)))
    add("el factor de la ampliación no es el cociente de sus extremos", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__(
            "factor_ampliacion", 41.7394173)))
    add("la tabla del techo cambia de alcance sin decirlo", "datos",
        m(lambda o: o["n_efectivo"]["techo"].__setitem__("phi", 8)))

    # --- 16. El puente de phi al factor, del módulo 4 (T2.2) -------------
    #
    # El módulo publica DOS cocientes que se parecen —49.63003 y 61.74778— y
    # antes los llamaba igual. Ahora tienen nombre propio, y estas
    # inyecciones atacan lo que los distingue.
    #
    # La tercera es la que justifica el gasto de rehacer 1'R1 con numpy:
    # mueve n_eff Y efecto_diseno a la vez, dejándolos CONSISTENTES entre
    # sí. Contra una comprobación que solo dividiera `n/n_eff` pasaría
    # limpia, porque la división sigue cuadrando; solo la reconstrucción
    # desde la matriz de correlación puede verla.
    add("la correlación en diagonal no es la de h = sqrt(2)", "datos",
        m(lambda o: o["inferencia"]["rejilla"][4].__setitem__(
            "rho_diagonal", 0.7413971)))
    add("el efecto de diseño no es el de su matriz de correlación", "datos",
        m(lambda o: o["inferencia"]["rejilla"][4].__setitem__(
            "efecto_diseno", 41.739417)))
    add("n_eff y el efecto de diseño se mueven juntos y siguen cuadrando", "datos",
        m(lambda o: (o["inferencia"]["rejilla"][4].__setitem__("n_eff", 6.0),
                     o["inferencia"]["rejilla"][4].__setitem__(
                         "efecto_diseno", 256 / 6.0))))
    add("la inflación de varianza deja de ser el factor al cuadrado", "datos",
        m(lambda o: o["inferencia"]["rejilla"][4].__setitem__(
            "inflacion_varianza", 41.739417)))
    add("E[s^2] no sale de la fórmula que el módulo publica", "datos",
        m(lambda o: o["inferencia"]["rejilla"][4].__setitem__(
            "s2_esperada", 0.6417394)))
    add("la s^2 simulada se aleja de la teórica", "datos",
        m(lambda o: o["inferencia"]["rejilla"][6].__setitem__(
            "s2_medida", 0.9417394)))
    add("la copia de cierre del efecto de diseño no es la de su fila", "datos",
        m(lambda o: o["inferencia"].__setitem__("efecto_diseno_phi4", 41.739417)))
    add("con phi=4 la desigualdad entre los dos cocientes se invierte", "datos",
        m(lambda o: (o["inferencia"].__setitem__("inflacion_varianza_phi4", 30.417394),
                     o["inferencia"]["rejilla"][4].__setitem__(
                         "inflacion_varianza", 30.417394),
                     o["inferencia"]["rejilla"][4].__setitem__(
                         "factor", 30.417394 ** 0.5))))
    add("E[s^2] deja de ser menor que sigma^2", "datos",
        m(lambda o: (o["inferencia"].__setitem__("s2_esperada_phi4", 1.4173941),
                     o["inferencia"]["rejilla"][4].__setitem__(
                         "s2_esperada", 1.4173941))))
    add("la escala de h deja de estar declarada", "datos",
        m(lambda o: o["inferencia"].__setitem__("escala_h", "   ")))
    add("la varianza marginal declarada deja de ser 1", "datos",
        m(lambda o: o["inferencia"].__setitem__("sigma", 4.1739)))

    # --- 9 y 10. A nivel de texto ----------------------------------------
    D.append(("una tilde convertida en bytes crudos", "datos", "txt",
              ("Deserción", "Deserci<c3><b3>n")))
    D.append(("un carácter de reemplazo U+FFFD", "datos", "txt",
              ("temperatura media", "temperatura m�dia")))
    D.append(("un flotante con más decimales de los declarados", "datos", "txt",
              ('"media": 3.4', '"media": 3.417394173941739, "media_vieja": 3.4')))
    D.append(("un NaN se cuela en el JSON", "datos", "txt",
              ('"sd": ', '"sd_roto": NaN, "sd": ')))

    # --- 11. Lo que se ve en cada mapa (2026-11-02) --------------------
    # La descripción larga dice DÓNDE pasa algo; un dato con otro nombre o en
    # otra zona no cambia ninguna cifra de la prosa y pone la frase en falso.
    add("la deserción más alta cambia de departamento", "datos",
        m(lambda o: o["visto"]["desercion"]["mayores"][0].__setitem__("departamento", "Vichada")))
    add("la deserción más baja cambia de zona", "datos",
        m(lambda o: o["visto"]["desercion"]["menores"][0].__setitem__("zona", "sur")))
    add("la clase alta de Carolina del Norte cambia de zona", "datos",
        m(lambda o: o["visto"]["nc"]["zona"].__setitem__(0, "suroriente")))
    add("la clase alta de Carolina del Norte gana condados", "datos",
        m(lambda o: o["visto"]["nc"].__setitem__("clase_alta_n", 23)))
    add("las estaciones frías se corren de zona", "datos",
        m(lambda o: o["visto"]["ideam"]["frias"]["n"].__setitem__(0, 25)))
    add("el umbral de las estaciones cálidas se corre", "datos",
        m(lambda o: o["visto"]["ideam"].__setitem__("calidas_umbral", 27.9)))
    add("las sedes de Bogotá cambian de franja", "datos",
        m(lambda o: o["visto"]["bogota"]["n"].__setitem__(1, 135)))
    add("el mapa de deserción vuelve a nombrar Bogotá en inglés", "mapas",
        m(lambda o: o["desercion"]["etiquetas"].__setitem__(
            o["desercion"]["etiquetas"].index("Bogotá D. C."), "Bogota Capital District")))

    # --- R2 · T2.4: las tres gráficas nuevas, un mutante por campo --------
    #
    # Cada campo que R publica para la prueba de aleatorización (módulo 1),
    # la envolvente de permutación (módulo 3) y los cien intervalos (módulo
    # 4) se rompe por separado. Los prefijos «R2 · T2.4» permiten correr solo
    # esta tanda (`--solo "R2 · T2.4"`).
    al_ = lambda o: o["snow"]["aleatorizacion"]                      # noqa: E731
    ev_ = lambda o: o["tobler"]["envolvente"]                        # noqa: E731
    ci_ = lambda o: o["inferencia"]["cien_ic"]                       # noqa: E731
    inf_ = lambda o: o["inferencia"]                                 # noqa: E731

    def pon(f, campo, valor):
        return m(lambda o: f(o).__setitem__(campo, valor(f(o)[campo]) if callable(valor) else valor))

    def en_lista(f, campo, i, valor):
        return m(lambda o: f(o)[campo].__setitem__(
            i, valor(f(o)[campo][i]) if callable(valor) else valor))

    # Módulo 1 · snow.aleatorizacion
    add("R2 · T2.4 · m1: las recolocaciones no son las del histograma", "datos",
        pon(al_, "n_recolocaciones", lambda v: v - 1))
    add("R2 · T2.4 · m1: la semilla de la nula es la del guion", "datos",
        m(lambda o: al_(o).__setitem__("semilla", o["meta"]["semilla"])))
    add("R2 · T2.4 · m1: los tramos de calle no son los del plano", "datos",
        pon(al_, "n_tramos", lambda v: v + 3))
    add("R2 · T2.4 · m1: dos bombas cambian de sitio en la lista", "datos",
        m(lambda o: al_(o).__setitem__("bombas", al_(o)["bombas"][1:2] + al_(o)["bombas"][0:1]
                                       + al_(o)["bombas"][2:])))
    add("R2 · T2.4 · m1: la parte de calle de una bomba cambia", "datos",
        en_lista(al_, "pct_calle_por_bomba", 3, lambda v: v + 0.4173))
    add("R2 · T2.4 · m1: la parte de calle de Broad St cambia", "datos",
        pon(al_, "pct_calle_broad", lambda v: v + 0.4173))
    add("R2 · T2.4 · m1: el cociente sobre la parte de calle no cuadra", "datos",
        pon(al_, "razon_sobre_calle", 6.41739))
    add("R2 · T2.4 · m1: la media de la nula no es la del histograma", "datos",
        pon(al_, "media_nula_pct", lambda v: v + 0.0041739))
    add("R2 · T2.4 · m1: el error de Monte Carlo de la nula cambia", "datos",
        pon(al_, "emc_media_pct", lambda v: v * 3))
    add("R2 · T2.4 · m1: la desviación típica de la nula cambia", "datos",
        pon(al_, "sd_nula_pct", lambda v: v * 1.2))
    add("R2 · T2.4 · m1: la desviación típica binomial cambia", "datos",
        pon(al_, "sd_binomial_pct", lambda v: v * 1.2))
    add("R2 · T2.4 · m1: el mínimo de la nula se corre una muerte", "datos",
        pon(al_, "min_nula_n", lambda v: v + 1))
    add("R2 · T2.4 · m1: el máximo de la nula se corre una muerte", "datos",
        pon(al_, "max_nula_n", lambda v: v - 1))
    add("R2 · T2.4 · m1: el mínimo en porcentaje no es su recuento", "datos",
        pon(al_, "min_nula_pct", lambda v: v + 0.17301))
    add("R2 · T2.4 · m1: el máximo en porcentaje no es su recuento", "datos",
        pon(al_, "max_nula_pct", lambda v: v + 0.17301))
    add("R2 · T2.4 · m1: una recolocación pasa a alcanzar al observado", "datos",
        pon(al_, "n_mayor_o_igual", 1))
    add("R2 · T2.4 · m1: la cota del valor p deja de ser 1/(B + 1)", "datos",
        pon(al_, "p_cota", 0.0))
    add("R2 · T2.4 · m1: el observado se acerca a la nula", "datos",
        pon(al_, "z_observado", 4.17391))
    add("R2 · T2.4 · m1: el histograma se corre un recuento", "datos",
        m(lambda o: al_(o).__setitem__("hist_n", [k + 1 for k in al_(o)["hist_n"]])))
    add("R2 · T2.4 · m1: dos barras del histograma se intercambian", "datos",
        m(lambda o: al_(o)["hist_frec"].__setitem__(
            slice(5, 30, 24), [al_(o)["hist_frec"][29], al_(o)["hist_frec"][5]])))
    add("R2 · T2.4 · m1: la curva binomial se desvía en una barra", "datos",
        en_lista(al_, "hist_binomial", 20, lambda v: v * 1.05))

    # Módulo 3 · tobler.envolvente
    add("R2 · T2.4 · m3: la envolvente declara menos permutaciones", "datos",
        pon(ev_, "nperm", 999))
    add("R2 · T2.4 · m3: el nivel de la envolvente cambia", "datos", pon(ev_, "nivel", 0.9))
    add("R2 · T2.4 · m3: el nivel en porcentaje no es el nivel", "datos", pon(ev_, "nivel_pct", 99))
    add("R2 · T2.4 · m3: el cuantil inferior no es el del nivel", "datos",
        pon(ev_, "cuantil_lo_pct", 5))
    add("R2 · T2.4 · m3: el cuantil superior no es el del nivel", "datos",
        pon(ev_, "cuantil_hi_pct", 95))
    add("R2 · T2.4 · m3: el estadístico de orden inferior cambia", "datos",
        pon(ev_, "orden_lo", lambda v: v + 1))
    add("R2 · T2.4 · m3: el estadístico de orden superior cambia", "datos",
        pon(ev_, "orden_hi", lambda v: v - 1))
    add("R2 · T2.4 · m3: las dos envolventes comparten semilla", "datos",
        m(lambda o: ev_(o).__setitem__("semilla_residuos", ev_(o)["semilla_ideam"])))
    add("R2 · T2.4 · m3: la semilla de la temperatura es la del guion", "datos",
        m(lambda o: ev_(o).__setitem__("semilla_ideam", o["meta"]["semilla"])))
    eb_ = lambda serie, i: (lambda o: ev_(o)[serie][i])              # noqa: E731
    add("R2 · T2.4 · m3: una banda de la envolvente empieza en otro sitio", "datos",
        pon(eb_("ideam", 2), "d1", lambda v: v + 5))
    add("R2 · T2.4 · m3: una banda de la envolvente acaba en otro sitio", "datos",
        pon(eb_("residuos_altitud", 4), "d2", lambda v: v + 25))
    add("R2 · T2.4 · m3: el borde inferior de la franja se encoge", "datos",
        pon(eb_("ideam", 0), "lo", lambda v: v * 0.5))
    add("R2 · T2.4 · m3: el borde superior de la franja se ensancha", "datos",
        pon(eb_("residuos_altitud", 3), "hi", lambda v: v * 1.6))
    add("R2 · T2.4 · m3: la franja deja de estar centrada en E[I]", "datos",
        pon(eb_("ideam", 5), "media", lambda v: v + 0.001))
    add("R2 · T2.4 · m3: el error de Monte Carlo de una banda cambia", "datos",
        pon(eb_("ideam", 1), "emc", lambda v: v * 1.5))
    add("R2 · T2.4 · m3: la desviación típica de una banda cambia", "datos",
        pon(eb_("residuos_altitud", 6), "sd", lambda v: v * 1.25))
    add("R2 · T2.4 · m3: el mínimo de las permutaciones baja hasta el dato", "datos",
        pon(eb_("ideam", 5), "min", -0.0941739))
    add("R2 · T2.4 · m3: el máximo de las permutaciones se dispara", "datos",
        pon(eb_("ideam", 6), "max", 0.0941739))
    add("R2 · T2.4 · m3: la última banda pasa a quedar «por debajo»", "datos",
        pon(eb_("ideam", 6), "posicion", "debajo"))
    add("R2 · T2.4 · m3: los residuos de 175-300 km pasan a «por encima»", "datos",
        pon(eb_("residuos_altitud", 4), "posicion", "encima"))
    add("R2 · T2.4 · m3: el recuento de bandas fuera (temperatura) cambia", "datos",
        pon(ev_, "n_fuera_ideam", 5))
    add("R2 · T2.4 · m3: el recuento de bandas fuera (residuos) cambia", "datos",
        pon(ev_, "n_fuera_residuos", 7))
    add("R2 · T2.4 · m3: la permutación suelta se sale en una banda", "datos",
        en_lista(ev_, "posicion_permutado", 2, "encima"))
    add("R2 · T2.4 · m3: el recuento de la permutación suelta cambia", "datos",
        pon(ev_, "n_fuera_permutado", 1))
    # Y el dato bajo la envolvente: la I de la banda negativa se mete dentro.
    add("R2 · T2.4 · m3: la banda negativa se mete en la franja", "datos",
        m(lambda o: o["tobler"]["ideam"]["bandas"][5].__setitem__("I", -0.0041739)))

    # Módulo 4 · inferencia.cien_ic
    add("R2 · T2.4 · m4: los cien intervalos son de otro alcance", "datos", pon(ci_, "phi", 2))
    add("R2 · T2.4 · m4: los cien intervalos dicen ser noventa y nueve", "datos",
        pon(ci_, "n", 99))
    add("R2 · T2.4 · m4: una media se va a cinco desviaciones", "datos",
        en_lista(ci_, "media", 0, 5.41739))
    add("R2 · T2.4 · m4: un semiancho ingenuo se ensancha", "datos",
        en_lista(ci_, "semiancho_ingenuo", 0, 3.41739))
    add("R2 · T2.4 · m4: el recuento ingenuo no es el de sus intervalos", "datos",
        pon(ci_, "n_cubren_ingenuo", lambda v: v + 1))
    add("R2 · T2.4 · m4: el semiancho medio no es la media de los cien", "datos",
        pon(ci_, "semiancho_ingenuo_medio", lambda v: v * 1.1))
    add("R2 · T2.4 · m4: el cuantil normal cambia", "datos", pon(ci_, "z_critico", 1.6448536))
    add("R2 · T2.4 · m4: el error estándar verdadero no sale de 1'R1", "datos",
        pon(ci_, "ee_exacto", lambda v: v * 1.05))
    add("R2 · T2.4 · m4: el semiancho exacto no es z por el e.e.", "datos",
        pon(ci_, "semiancho_exacto", lambda v: v * 0.9))
    add("R2 · T2.4 · m4: el recuento exacto no es el de sus intervalos", "datos",
        pon(ci_, "n_cubren_exacto", lambda v: v - 1))
    add("R2 · T2.4 · m4: el cociente de semianchos no cuadra", "datos",
        pon(ci_, "razon_semianchos", 6.41739))
    add("R2 · T2.4 · m4: la cobertura exacta deja de ser la nominal", "datos",
        pon(ci_, "cobertura_exacto", 0.91))
    add("R2 · T2.4 · m4: el error de la cobertura exacta no es el suyo", "datos",
        pon(ci_, "emc_cobertura_exacto", lambda v: v * 2))

    # Segunda ronda de T2.4: el marco del plano, las parejas que el eje deja
    # fuera, la suma por bandas, «alguna banda fuera» y el nivel.
    mr_ = lambda i: (lambda o: al_(o)["marcos"][i])                  # noqa: E731
    mx_ = lambda o: o["tobler"]["mas_alla"]                          # noqa: E731
    sm_ = lambda o: o["tobler"]["sumas"]                             # noqa: E731
    add("R2 · T2.4 · r2 m1: la caja de las muertes se ensancha", "datos",
        en_lista(al_, "caja_muertes", 1, lambda v: v + 0.5))
    add("R2 · T2.4 · r2 m1: la caja de las calles se encoge", "datos",
        en_lista(al_, "caja_calles", 0, lambda v: v + 0.5))
    add("R2 · T2.4 · r2 m1: un marco cambia de nombre", "datos",
        pon(mr_(0), "marco", "el plano entero"))
    add("R2 · T2.4 · r2 m1: un marco cambia de margen", "datos", pon(mr_(1), "margen", 3))
    add("R2 · T2.4 · r2 m1: la calle que entra en un marco cambia", "datos",
        pon(mr_(2), "pct_longitud", lambda v: v + 1.41739))
    add("R2 · T2.4 · r2 m1: la parte de calle del marco estrecho cambia", "datos",
        pon(mr_(0), "pct_calle_broad", lambda v: v - 1.41739))
    add("R2 · T2.4 · r2 m1: la razón de un marco no es su cociente", "datos",
        pon(mr_(1), "razon_sobre_calle", 4.41739))
    add("R2 · T2.4 · r2 m1: con el marco estrecho el dato se acerca a la nula", "datos",
        pon(mr_(0), "z_binomial", 4.17391))
    add("R2 · T2.4 · r2 m3: lo de más allá del eje empieza en otra distancia", "datos",
        pon(mx_, "d1", 700))
    add("R2 · T2.4 · r2 m3: la distancia máxima de la red cambia", "datos",
        pon(mx_, "d_max", lambda v: v + 41.739))
    add("R2 · T2.4 · r2 m3: las parejas de más allá del eje cambian", "datos",
        pon(mx_, "n_pares", lambda v: v + 7))
    add("R2 · T2.4 · r2 m3: las parejas de la red entera cambian", "datos",
        pon(mx_, "n_pares_total", lambda v: v + 361))
    add("R2 · T2.4 · r2 m3: el porcentaje de parejas fuera del eje cambia", "datos",
        pon(mx_, "pct_pares", 11.41739))
    add("R2 · T2.4 · r2 m3: no todas las estaciones tienen pareja lejana", "datos",
        pon(mx_, "n_con_vecinos", lambda v: v - 4))
    add("R2 · T2.4 · r2 m3: la I de más allá del eje cambia", "datos",
        pon(mx_, "I", lambda v: v + 0.0141739))
    add("R2 · T2.4 · r2 m3: el borde inferior de esa franja se encoge", "datos",
        pon(mx_, "lo", lambda v: v * 0.5))
    add("R2 · T2.4 · r2 m3: el borde superior de esa franja se ensancha", "datos",
        pon(mx_, "hi", lambda v: v * 1.6))
    add("R2 · T2.4 · r2 m3: esa franja deja de centrarse en E[I]", "datos",
        pon(mx_, "media", lambda v: v + 0.002))
    add("R2 · T2.4 · r2 m3: la desviación típica de esa franja cambia", "datos",
        pon(mx_, "sd", lambda v: v * 1.25))
    add("R2 · T2.4 · r2 m3: lo de más allá del eje pasa a quedar dentro", "datos",
        pon(mx_, "posicion", "dentro"))
    sb_ = lambda i: (lambda o: sm_(o)["bandas"][i])                  # noqa: E731
    add("R2 · T2.4 · r2 m3: una suma va sobre otra banda", "datos", pon(sb_(2), "d2", 110))
    add("R2 · T2.4 · r2 m3: una suma empieza en otro sitio", "datos", pon(sb_(3), "d1", 90))
    add("R2 · T2.4 · r2 m3: las parejas de una suma cambian", "datos",
        pon(sb_(4), "n_pares", lambda v: v + 5))
    add("R2 · T2.4 · r2 m3: la suma de la banda negativa cambia", "datos",
        pon(sb_(5), "suma", lambda v: v + 1.41739))
    add("R2 · T2.4 · r2 m3: la suma de más allá del eje cambia", "datos",
        pon(sm_, "mas_alla", lambda v: v - 0.41739))
    add("R2 · T2.4 · r2 m3: las bandas cortas pasan a ser cuatro", "datos",
        pon(sm_, "n_bandas_cortas", 4))
    add("R2 · T2.4 · r2 m3: la suma de las bandas cortas cambia", "datos",
        pon(sm_, "cortas", lambda v: v + 0.41739))
    add("R2 · T2.4 · r2 m3: la suma de todo lo demás cambia", "datos",
        pon(sm_, "largas", lambda v: v + 0.41739))
    add("R2 · T2.4 · r2 m3: el total de las sumas deja de ser -1", "datos", pon(sm_, "total", -0.9))
    add("R2 · T2.4 · r2 m3: casi ninguna permutación se sale en alguna banda", "datos",
        pon(ev_, "pct_alguna_fuera", 4.17391))
    add("R2 · T2.4 · r2 m3: el error de «alguna banda fuera» no es el suyo", "datos",
        pon(ev_, "emc_alguna_fuera_pct", lambda v: v * 2))
    add("R2 · T2.4 · r2 m4: el nivel de los intervalos no es el de alfa", "datos",
        pon(inf_, "nivel_pct", 90))

    # --- R2 · T2.2: las gráficas y los mapas propios del capítulo -------
    def _cambia(lista, i, j):
        lista[i], lista[j] = lista[j], lista[i]

    def _otro_pliegue(o, clave):
        v = o["ideam"][clave]
        j = next(k for k in range(1, len(v)) if v[k] != v[0])
        v[0], v[j] = v[j], v[0]

    add("R2 · T2.2 · Snow: desaparecen las celdas de las bombas", "mapas",
        m(lambda o: o["snow"].pop("celdas")))
    add("R2 · T2.2 · Snow: dos bombas se cambian la celda", "mapas",
        m(lambda o: _cambia(o["snow"]["celdas"], 6, 5)))
    add("R2 · T2.2 · Snow: la celda de Broad St crece hacia un lado", "mapas",
        m(lambda o: o["snow"]["celdas"][6].__setitem__(0, o["snow"]["celdas"][6][0] + 400)))
    add("R2 · T2.2 · Snow: falta una celda", "mapas",
        m(lambda o: o["snow"]["celdas"].pop()))
    add("R2 · T2.2 · Snow: vuelve el pie de leyenda bajo las entradas", "mapas",
        m(lambda o: o["snow"].__setitem__("leyenda", "bomba más próxima")))
    add("R2 · T2.2 · Mosa: la rampa vuelve a ser lineal", "mapas",
        m(lambda o: o["meuse"].pop("marcas_escala")))
    add("R2 · T2.2 · Mosa: el marco ya no es el de los puntos", "mapas",
        m(lambda o: o["meuse"]["caja"].__setitem__(0, o["meuse"]["caja"][0] - 300)))
    add("R2 · T2.2 · Mosa: se pierde una orilla", "mapas",
        m(lambda o: o["meuse"]["lineas"].pop()))
    add("R2 · T2.2 · Mosa: el río dibujado es otro", "mapas",
        m(lambda o: o["meuse"].__setitem__("lineas", [[4096 - v if i % 2 == 0 else v for i, v in enumerate(l)]
                                                    for l in o["meuse"]["lineas"]])))
    add("R2 · T2.2 · m7: la ventana del acercamiento se corre", "mapas",
        m(lambda o: o["agregacion"]["zoom"]["caja"].__setitem__(0, o["agregacion"]["zoom"]["caja"][0] + 150000)))
    add("R2 · T2.2 · m7: el acercamiento declara otras celdas", "mapas",
        m(lambda o: o["agregacion"]["zoom"].__setitem__("n_celdas", 25)))
    add("R2 · T2.2 · m7: desaparece la ventana del acercamiento", "mapas",
        m(lambda o: o["agregacion"].pop("zoom")))
    add("R2 · T2.2 · IDEAM: desaparece el contorno del país", "mapas",
        m(lambda o: o["ideam"].pop("lineas")))
    add("R2 · T2.2 · IDEAM: el contorno es de otro sitio", "mapas",
        m(lambda o: o["ideam"].__setitem__("lineas", [[v // 2 for v in l] for l in o["ideam"]["lineas"]])))
    add("R2 · T2.2 · IDEAM: una franja de altitud cuenta de más", "datos",
        m(lambda o: o["visto"]["ideam"]["por_altitud"][2].__setitem__(
            "n", o["visto"]["ideam"]["por_altitud"][2]["n"] + 1)))
    add("R2 · T2.2 · IDEAM: la temperatura media de una franja cambia", "datos",
        m(lambda o: o["visto"]["ideam"]["por_altitud"][4].__setitem__("t_media", 16.41739)))
    add("R2 · T2.2 · IDEAM: desaparecen las franjas de altitud", "datos",
        m(lambda o: o["visto"]["ideam"].pop("por_altitud")))
    add("R2 · T2.2 · m10: dos estaciones se cambian de pliegue al azar", "mapas",
        m(lambda o: _otro_pliegue(o, "pliegue_aleatorio")))
    add("R2 · T2.2 · m10: dos estaciones se cambian de bloque", "mapas",
        m(lambda o: _otro_pliegue(o, "pliegue_bloques")))
    add("R2 · T2.2 · m10: el mapa pierde un reparto", "mapas",
        m(lambda o: o["ideam"].pop("pliegue_bloques")))
    add("R2 · T2.2 · m10: las vecinas en su pliegue, al azar, cambian", "datos",
        m(lambda o: o["cv_espacial"].__setitem__("vecina_en_su_pliegue_aleatoria", 37)))
    add("R2 · T2.2 · m10: las vecinas en su bloque cambian", "datos",
        m(lambda o: o["cv_espacial"].__setitem__("vecina_en_su_pliegue_bloques", 340)))
    add("R2 · T2.2 · m10: el RMSE aleatorio no es el de sus pliegues", "datos",
        m(lambda o: (o["cv_espacial"].__setitem__("rmse_aleatoria", o["cv_espacial"]["rmse_aleatoria"] * 1.001),
                     o["cv_espacial"].__setitem__("razon", o["cv_espacial"]["rmse_bloques"] / (o["cv_espacial"]["rmse_aleatoria"])),
                     o["cv_espacial"].__setitem__("inflacion_pct", 100 * (o["cv_espacial"]["razon"] - 1)),
                     o["cv_espacial"].__setitem__("r2_aleatoria", 1 - o["cv_espacial"]["rmse_aleatoria"] ** 2 / o["cv_espacial"]["sd_variable"] ** 2))))
    add("R2 · T2.2 · m4: un campo pierde el centro de su escala", "mapas",
        m(lambda o: o["campos"][2].pop("centro")))
    add("R2 · T2.2 · m4: los cortes de un campo dejan de ser simétricos", "mapas",
        m(lambda o: o["campos"][4]["cortes"].__setitem__(0, o["campos"][4]["cortes"][0] - 0.5)))
    add("R2 · T2.2 · m4: un campo va con otra escala que los demás", "mapas",
        m(lambda o: o["campos"][1].__setitem__("rango", [-3.5, 3.5])))
    add("R2 · T2.2 · m4: las celdas por clase de un campo cambian", "mapas",
        m(lambda o: (o["campos"][4]["tam"].__setitem__(2, o["campos"][4]["tam"][2] + 9),
                     o["campos"][4]["tam"].__setitem__(3, o["campos"][4]["tam"][3] - 9))))
    add("R2 · T2.2 · m4: un campo pierde su recuento por clase", "mapas",
        m(lambda o: o["campos"][0].pop("tam")))
    add("R2 · T2.2 · m4: la media del campo destacado no es la de la réplica 1", "mapas",
        m(lambda o: o["campos"][4].__setitem__("media_espacial", o["campos"][4]["media_espacial"] + 0.05)))
    add("R2 · T2.2 · m4: la réplica 1 de los cien intervalos es otra", "datos",
        m(lambda o: o["inferencia"]["cien_ic"]["media"].__setitem__(
            0, o["inferencia"]["cien_ic"]["media"][0] + 0.0004)))
    add("R2 · T2.2 · m4: el I de Moran de un campo no es el de su mapa", "mapas",
        m(lambda o: o["campos"][5].__setitem__("moran", o["campos"][5]["moran"] + 0.02)))
    add("R2 · T2.2 · m4: un campo vuelve a la rejilla de 28×28", "mapas",
        m(lambda o: (o["campos"][3].__setitem__("nx", 28), o["campos"][3].__setitem__("ny", 28))))
    add("R2 · T2.2 · m6: una realización pierde el centro de su escala", "mapas",
        m(lambda o: o["realizaciones"][0].__setitem__("centro", 0.3)))
    add("R2 · T2.2 · m6: las celdas por clase de una realización cambian", "mapas",
        m(lambda o: (o["realizaciones"][2]["tam"].__setitem__(1, o["realizaciones"][2]["tam"][1] + 12),
                     o["realizaciones"][2]["tam"].__setitem__(5, o["realizaciones"][2]["tam"][5] - 12))))
    add("R2 · T2.2 · m6: el recorrido común no es el de las tres", "mapas",
        m(lambda o: [g.__setitem__("rango", [-3.0, 3.0]) or g.__setitem__(
            "cortes", [-3.0 + 6.0 * k / 7 for k in range(8)]) for g in o["realizaciones"]]))

    # --- R2 · T2.3: los bordes de Bogotá y la caja de los pinos ----------
    add("R2 · T2.3 · Bogotá: el área del rectángulo de las sedes cambia", "datos",
        m(lambda o: o["colombia"]["puntual"].__setitem__("area_caja_km2", 4613.41739)))
    add("R2 · T2.3 · Bogotá: la intensidad con el rectángulo cambia", "datos",
        m(lambda o: o["colombia"]["puntual"].__setitem__("lambda_caja", 0.48417)))
    add("R2 · T2.3 · Bogotá: lo que el rectángulo se sale del Distrito cambia", "datos",
        m(lambda o: o["colombia"]["puntual"].__setitem__("pct_caja_fuera_dc", 61.7)))
    add("R2 · T2.3 · Bogotá: el mapa pierde sus bordes", "mapas",
        m(lambda o: o["bogota"].pop("bordes")))
    add("R2 · T2.3 · Bogotá: el perímetro urbano y el Distrito se cambian el nombre", "mapas",
        m(lambda o: o["bogota"]["bordes"].update(urbano=o["bogota"]["bordes"]["distrito"],
                                                 distrito=o["bogota"]["bordes"]["urbano"])))
    add("R2 · T2.3 · Bogotá: el rectángulo dibujado no es el de las sedes", "mapas",
        m(lambda o: o["bogota"]["bordes"]["caja"][0].__setitem__(0, o["bogota"]["bordes"]["caja"][0][0] - 300)))
    add("R2 · T2.3 · Bogotá: una sede del perímetro urbano se lee como del resto del Distrito", "mapas",
        m(lambda o: o["bogota"]["dentro"].__setitem__(o["bogota"]["dentro"].index(2), 1)))
    add("R2 · T2.3 · Bogotá: el mapa pierde el borde de cada sede", "mapas",
        m(lambda o: o["bogota"].pop("dentro")))
    add("R2 · T2.3 · Bogotá: una sede urbana en el tercio del medio", "datos",
        m(lambda o: o["visto"]["bogota"]["urbana"].__setitem__(1, 1)))
    add("R2 · T2.3 · Bogotá: ninguna sede fuera del Distrito en el tercio del medio", "datos",
        m(lambda o: o["visto"]["bogota"]["fuera_dc"].__setitem__(1, 0)))
    add("R2 · T2.3 · Bogotá: el perímetro urbano baja del corte", "datos",
        m(lambda o: o["visto"]["bogota"].__setitem__("margen_urbano_m", -5.0)))
    add("R2 · T2.3 · deserción: la clase más oscura, con otro reparto por zonas", "datos",
        m(lambda o: o["visto"]["desercion"]["clase_alta"]["zonas"]["n"].__setitem__(0, 4)))
    add("R2 · T2.3 · IDEAM: las más frías dejan de ser las que son", "datos",
        m(lambda o: o["visto"]["ideam"].__setitem__("n_frias", 36)))
    add("R2 · T2.3 · IDEAM: las más altas, con otro reparto por zonas", "datos",
        m(lambda o: o["visto"]["ideam"]["altas"]["zonas"]["n"].__setitem__(0, 30)))
    add("R2 · T2.3 · IDEAM: la temperatura baja otra cosa por km", "datos",
        m(lambda o: o["visto"]["ideam"].__setitem__("baja_por_km", 6.1)))
    add("R2 · T2.3 · meuse: el zinc alto, del lado sureste", "datos",
        m(lambda o: o["visto"]["meuse"].__setitem__("lado", "sureste")))
    add("R2 · T2.3 · meuse: el décimo alto cuenta otro número del lado noroeste", "datos",
        m(lambda o: o["visto"]["meuse"].__setitem__("top_noroeste", 10)))
    add("R2 · T2.3 · pinos: el área del rectángulo de los puntos cambia", "datos",
        m(lambda o: o["puntual_canonico"]["japanesepines"].__setitem__("area_caja", 0.93)))
    add("R2 · T2.3 · pinos: la intensidad con ese rectángulo cambia", "datos",
        m(lambda o: o["puntual_canonico"]["japanesepines"].__setitem__("lambda_caja", 70.41739)))

    return D


# =====================================================================
def corre(rutas: dict[str, pathlib.Path]) -> tuple[int, str]:
    entorno = dict(os.environ)
    for clave, ruta in rutas.items():
        entorno[ARCHIVOS[clave][0]] = str(ruta)
    res = subprocess.run([PY, str(AUDITOR)], capture_output=True, text=True,
                         cwd=str(RAIZ), env=entorno)
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


def main() -> int:
    for _, nombre in ARCHIVOS.values():
        if not (SALIDAS / nombre).exists():
            print(f"PARADO: falta {SALIDAS / nombre}. Ejecuta antes "
                  f"genera_cap1.R y genera_soluciones.R")
            return 1

    originales = {c: (SALIDAS / n).read_bytes() for c, (_, n) in ARCHIVOS.items()}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="prueba_auditor_cap1_"))
    limpias = {}
    for clave, (_, nombre) in ARCHIVOS.items():
        limpias[clave] = tmp / nombre
        shutil.copy(SALIDAS / nombre, limpias[clave])

    print("=" * 66)
    print("  prueba_auditor_cap1.py — el arnés de inyección del capítulo 1")
    print("=" * 66)

    # --- CONTROL DE ENTRADA ------------------------------------------
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

    lista = defectos()
    # `--solo PREFIJO` corre solo los defectos cuyo nombre empieza así: sirve
    # para probar una tanda nueva sin esperar a las demás. La pasada completa
    # —sin argumentos— es la que cuenta para dar algo por cerrado.
    if "--solo" in sys.argv:
        prefijo = sys.argv[sys.argv.index("--solo") + 1]
        lista = [d for d in lista if d[0].startswith(prefijo)]
    cazados = 0
    print(f"\n  {len(lista)} defectos que inyectar\n" + "-" * 66)

    for nombre_d, clave, tipo, accion in lista:
        rutas = dict(limpias)
        rota = tmp / f"roto_{ARCHIVOS[clave][1]}"
        if tipo == "obj":
            obj = json.loads(limpias[clave].read_text(encoding="utf-8"))
            antes = json.dumps(obj, ensure_ascii=False, sort_keys=True)
            accion(obj)
            despues = json.dumps(obj, ensure_ascii=False, sort_keys=True)
            if antes == despues:
                # Una inyección que no cambia nada registraría un «no
                # detectado» que es culpa del arnés, no del auditor.
                print(f"  MAL  {nombre_d}")
                print(f"        la mutación no cambió el archivo")
                continue
            rota.write_text(json.dumps(obj, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        else:
            busca, pone = accion
            txt = limpias[clave].read_text(encoding="utf-8")
            if txt.count(busca) < 1:
                print(f"  MAL  {nombre_d}")
                print(f"        el texto a sustituir no aparece: {busca[:60]!r}")
                continue
            rota.write_text(txt.replace(busca, pone, 1), encoding="utf-8")
        rutas[clave] = rota

        codigo, salida = corre(rutas)
        ok = codigo != 0
        cazados += ok
        print(f"  {'OK ' if ok else 'MAL'}  {nombre_d}")
        print(f"        {resumen(salida)}")
        if ok:
            vistas_fallar |= nombres(salida, "MAL")
        else:
            print(f"        NO DETECTADO — el auditor dio el archivo por bueno")

    # --- CONTROL DE SALIDA -------------------------------------------
    codigo, salida = corre(limpias)
    print("\n" + "-" * 66)
    print(f"  {'OK ' if codigo == 0 else 'MAL'}  control de salida · el arnés no dejó nada tocado")
    intactos = all((SALIDAS / n).read_bytes() == originales[c]
                   for c, (_, n) in ARCHIVOS.items())
    print(f"  {'OK ' if intactos else 'MAL'}  los archivos publicados siguen byte a byte igual")

    shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 66)
    print(f"  {cazados} de {len(lista)} defectos cazados")
    print(f"  {len(vistas_fallar)} de {len(todas)} comprobaciones se han visto fallar")
    if todas - vistas_fallar:
        # La pregunta incómoda: de las que nunca han fallado, ¿cuáles son
        # comprobaciones legítimas que este arnés no ejercita y cuáles son
        # incapaces de fallar? Se imprimen agrupadas para poder mirarlas.
        restantes = sorted(todas - vistas_fallar)
        print(f"\n  Sin ver fallar ({len(restantes)}). La mayoría son otras "
              f"instancias de\n  mecanismos ya demostrados —otro dato, otro "
              f"lag, otro par—, pero\n  la lista se imprime para que nadie "
              f"tenga que fiarse de eso:")
        for r in restantes[:20]:
            print(f"    · {r}")
        if len(restantes) > 20:
            print(f"    · … y {len(restantes) - 20} más")
    print("=" * 66)

    fallos = (cazados != len(lista)) or codigo != 0 or not intactos
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
