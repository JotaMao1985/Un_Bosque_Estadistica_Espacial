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
    add("E3: el techo deja de ser 1/rho", "soluciones",
        m(lambda o: o["e3"]["solucion"].__setitem__("techo", 41.73914)))
    add("E4: la r deja de crecer con el tamaño de la unidad", "soluciones",
        m(lambda o: o["e4"]["solucion"]["conglomerado"].__setitem__("r", 0.41739)))
    add("E4: la r municipal deja de ser la del módulo 7", "soluciones",
        m(lambda o: o["e4"]["solucion"]["municipal"].__setitem__("r", 0.4173941)))

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

    # --- 15. Los dos rho del módulo 5 (T2.1) -----------------------------
    #
    # El módulo publica un rho DESPEJADO y un rho MEDIDO, y la gracia está en
    # su distancia. Las inyecciones atacan las dos naturalezas: el despeje se
    # rompe rompiendo el álgebra, y la medición se rompe tocando el
    # correlograma —los pares, las islas, la I— que el auditor rehace desde el
    # GeoPackage con geopandas. `islas` es el entero sin el cual esa
    # reconstrucción sería imposible: convierte la convención de spdep en la
    # de esda, y por eso también se inyecta.
    add("el rho implícito deja de ser el despeje", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "implicito", 0.0173941)))
    add("el rho estimado no es la media ponderada de sus bandas", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "estimado", 0.0041739)))
    add("una I de banda no es la que mide el mapa", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"]["bandas"][2].__setitem__(
            "I", 0.1739417)))
    add("los pares de una banda no son los que hay", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"]["bandas"][3].__setitem__(
            "pares", 41739)))
    add("las islas de una banda no son las que hay", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"]["bandas"][0].__setitem__(
            "islas", 41)))
    add("el n_eff que daría el rho medido está mal", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "n_eff_con_estimado", 417.3941)))
    add("la razón entre los dos rho no es su cociente", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "razon_rho", 4.173941)))
    add("los pares totales no suman los de las bandas", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "pares_totales", 417394)))
    add("los pares lejanos declarados no son los de I negativa", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "pares_lejanos", 41739)))
    add("la I de la primera banda que cita la prosa no es la suya", "datos",
        m(lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__(
            "I_primera_banda", 0.4173941)))

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
