#!/usr/bin/env python3
"""
prueba_auditor_apendicea.py — le rompe el precálculo al auditor del apéndice A
y exige que lo cace

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. Un auditor que informa «0 fallos» la primera vez no ha
demostrado nada: puede estar comprobando bien o puede estar comprobando
cosas incapaces de fallar. `audita_apendicea.py` dio 857 comprobaciones en
su primera pasada, y esa cifra no es la que vale: lo que vale es que en
esa pasada CAZÓ UN DEFECTO REAL —la masa con la corrección e(x) del
módulo 12 salía de una `integrate()` sobre [0, ∞) que pierde el pico de
las sedes lejanas: se publicaba 0.949 y es 0.991; el generador ya está
arreglado— y que aquí se demuestra que sabe fallar en cada familia.

La maquinaria vive en `prueba_auditor_base.py`. Aquí solo se declara QUÉ
romper, que es lo único propio del apéndice.

LAS FAMILIAS DE DEFECTO, y cada una imita algo que este apéndice puede
sufrir de verdad:

   0. el dato de partida o la semilla compartida (las mismas z en todas)
   1. el histograma de la cafetería y su intensidad
   2. el histograma de `faithful`: un conteo de modas que cambia
   3. el ASH que deja de acercarse al triangular, la trampa de las ventanas
   4. la ventana k/(nV), sus formas cerradas y la figura de Kennedy
   5. la KDE de juguete y sus modas
   6. los núcleos, y la muestra unimodal que NO se publica
   7. el k-NN: dientes, áreas que no paran de crecer
   8. sesgo, varianza y MISE en forma cerrada
   9. las reglas de referencia y el «silverman» de scipy
  10. la validación cruzada: selectores, modas, AIMSE
  11. el EM, la MISE de la mezcla y el MONTE CARLO (victorias, colas, CSV)
  12. las sedes: reciprocidad, empates, umbral, ln 2 en el borde, Diggle
  13. los ejercicios: un «pide» que deja de estar en su enunciado
 13b. los CSV que leen las pestañas de Python (cafetería, faithful, mezcla)
  14. formato: tildes, NA, decimales, metainformación

UNA INYECCIÓN NO PUEDE USAR UN VALOR QUE YA ESTÉ EN LOS ARCHIVOS. Si la
cifra falsa coincidiera con otra real, el auditor podría «cazarla» por el
motivo equivocado y el arnés se felicitaría solo. Aquí no se confía al
ojo: antes de inyectar nada, `valores_nuevos()` busca cada número
inyectado entre todos los de los siete archivos y PARA si lo encuentra.
Se eximen los enteros pequeños (un conteo de modas de 3 siempre coincide
con algún otro 3) y los valores que no son números.

Uso:  python3 precalculo/prueba_auditor_apendicea.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prueba_auditor_base import arnes                       # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_apendicea.py"

ARCHIVOS = {
    "datos": ("APA_DATOS", "apendicea_datos.json"),
    "soluciones": ("APA_SOLUCIONES", "apendicea_soluciones.json"),
    "mc": ("APA_MC", "apendicea_mc.csv"),
    "muestras": ("APA_MUESTRAS", "apendicea_mc_muestras.csv"),
    "cafeteria": ("APA_CAFETERIA", "apendicea_cafeteria.csv"),
    "faithful": ("APA_FAITHFUL", "apendicea_faithful.csv"),
    "mezcla": ("APA_MEZCLA", "apendicea_mezcla.csv"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]

INYECTADOS: list[tuple[str, object]] = []      # (defecto, valor) para valores_nuevos()


def _baja(o, k):
    """Un paso de la ruta: una clave, un índice o («campo», valor) en una lista."""
    if isinstance(k, tuple):
        return next(x for x in o if isinstance(x, dict) and x.get(k[0]) == k[1])
    return o[k]


def fija(ruta, valor):
    def accion(d):
        o = d
        for k in ruta[:-1]:
            o = _baja(o, k)
        o[ruta[-1]] = valor
    return accion


def lineas(nombre):
    return (SALIDAS / nombre).read_text(encoding="utf-8").splitlines()


def fila_csv(nombre, replica, columna, nuevo, ocurrencia=0):
    """(busca, pone) que cambia UNA celda de una fila del CSV, como texto.

    Se busca la fila entera, con su salto de línea delante, para que la
    sustitución no pueda caer en otra fila que empiece igual.
    """
    ls = lineas(nombre)
    cab = next(csv.reader([ls[0]]))
    j = cab.index(columna)
    filas = [l for l in ls[1:] if l.split(",")[0] == str(replica)]
    original = filas[ocurrencia]
    campos = original.split(",")
    campos[j] = nuevo
    return "\n" + original + "\n", "\n" + ",".join(campos) + "\n"


def linea_csv(nombre, i, columna, nuevo):
    """(busca, pone) que cambia una celda de la fila de datos i (desde 1).

    Si la fila no es única en el archivo —`faithful` repite parejas—, se
    pasa a la siguiente: una sustitución que cayera en otra fila igual
    rompería otra cosa de la que se dice.
    """
    ls = lineas(nombre)
    cab = next(csv.reader([ls[0]]))
    j = cab.index(columna)
    todo = "\n".join(ls) + "\n"
    while todo.count("\n" + ls[i] + "\n") != 1:
        i += 1
    campos = ls[i].split(",")
    campos[j] = nuevo
    return "\n" + ls[i] + "\n", "\n" + ",".join(campos) + "\n"


def defectos():
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D = []

    def obj(nombre, clave, ruta, valor):
        D.append((nombre, clave, "obj", fija(ruta, valor)))
        INYECTADOS.append((nombre, valor))

    def fn(nombre, clave, accion):
        D.append((nombre, clave, "obj", accion))

    def txt(nombre, clave, busca, pone, nuevo=None):
        D.append((nombre, clave, "txt", (busca, pone)))
        if nuevo is not None:
            INYECTADOS.append((nombre, nuevo))

    # --- 0. El dato de partida y la semilla compartida ------------------
    obj("0 · un dato de faithful cambia", "datos", ["m2", "eruptions", 17], 4.4131)
    obj("0 · la nube sale de otra semilla", "datos", ["m8", "nube", 0, 7], 1.713131)
    obj("0 · el área urbana cambia", "datos", ["m1", "sedes", "area_km2"], 371.3131)

    # --- 1. La cafetería ------------------------------------------------
    obj("1 · un conteo del histograma cambia", "datos", ["m1", "conteos", 2], 31)
    obj("1 · la cafetería pasa a tener tres modas", "datos", ["m1", "modas"], 3)
    obj("1 · λ de las sedes cambia", "datos", ["m1", "sedes", "lambda_km2"], 5.71313131)
    obj("1 · un tiempo de la cafetería cambia", "datos", ["m1", "tiempos", 3], 3.913131)

    # --- 2. El histograma de faithful -----------------------------------
    obj("2 · las modas máximas de un ancho cambian", "datos", ["m2", "modas_max", 3], 4)
    obj("2 · el ancho en que manda el origen cambia", "datos", ["m2", "h_origen"], 0.2713)
    obj("2 · los orígenes con pocas modas cambian", "datos",
        ["m2", "origen", "origenes_pocas"], 15)
    obj("2 · un corte del histograma por defecto cambia", "datos", ["m2", "def_cortes", 3], 3.1313)
    obj("2 · Freedman-Diaconis cambia de clases", "datos", ["m2", "fd", "clases"], 6)

    # --- 3. El ASH --------------------------------------------------------
    obj("3 · el ASH deja de acercarse al triangular con m", "datos",
        ["m3", "triangular", "distancia", 4], 0.0313131)
    obj("3 · la trampa de las ventanas da área 1", "datos", ["m3", "solapadas", "area"], 1.0)
    obj("3 · una f_j de la tabla a mano cambia", "datos", ["m3", "ejemplo", "f_j", 1, 2], 0.0713131)
    obj("3 · la malla base corrida ya no pierde datos", "datos",
        ["m3", "ejemplo", "base_desplazada_cuenta"], [8, 8, 8])
    obj("3 · el factor de varianza del ASH cambia", "datos", ["m3", "varianza", "factor", 2], 0.7131313)

    # --- 4. k / (nV) ------------------------------------------------------
    obj("4 · la ventana óptima con n = 400 cambia", "datos", ["m4", "por_n", 2, "v_opt"], 1.0713131)
    obj("4 · el sitio medio cuenta otras sedes", "datos",
        ["m4", "plano", "sitios", 1, "parzen_conteo"], 8)
    obj("4 · el radio k-NN del sitio ralo cambia", "datos",
        ["m4", "plano", "sitios", 2, "knn_radio"], 0.4713)
    obj("4 · un ECM de la ventana cambia", "datos", ["m4", "por_n", 0, "ecm", 30], 0.0313131)

    # --- 5. La KDE de juguete --------------------------------------------
    obj("5 · las modas de la KDE de juguete cambian", "datos", ["m5", "modas", "modas"], [5, 3, 2, 1])
    obj("5 · un término gaussiano cambia", "datos", ["m5", "gaussiano", "terminos", 1], 0.2413131)

    # --- 6. Los núcleos y la unimodal no publicada -----------------------
    obj("6 · la caja de la trimodal deja otras modas", "datos", ["m6", "trimodal", "modas_rect"], 71)
    obj("6 · la unimodal (no publicada) cambia de modas", "datos",
        ["m6", "unimodal", "modas_epan"], 11)
    obj("6 · el bw de la unimodal cambia", "datos", ["m6", "unimodal", "bw"], 0.7313131)
    obj("6 · R(K) del biweight cambia", "datos",
        ["m6", "nucleos", ("nombre", "biweight"), "RK"], 0.7131313)
    obj("6 · el cuártico del plano deja de valer 8", "datos", ["m6", "plano", "cuartico"], 7.9131313)

    # --- 7. k vecinos ----------------------------------------------------
    obj("7 · con k = 80 la curva se alisa", "datos", ["m7", "mezcla", "por_k", 5, "modas"], 9)
    obj("7 · el «globo» de las edades cambia", "datos", ["m7", "edades", "balloon"], 0.0613131)
    obj("7 · el área del k-NN deja de crecer", "datos",
        ["m7", "ingresos", "areas", 2, "area"], 1.5131313)
    obj("7 · el valle de la mezcla con k = 10 cambia", "datos",
        ["m7", "mezcla", "por_k", 2, "f_valle"], 0.0431313)

    # --- 8. Sesgo, varianza y MISE ---------------------------------------
    obj("8 · el h del MISE exacto cambia", "datos", ["m8", "h_mise"], 0.4313131)
    obj("8 · un ECM de la curva cambia", "datos", ["m8", "ecm", 40], 0.0213131)
    obj("8 · la varianza asintótica cambia", "datos", ["m8", "asintotica", "var_formula"], 0.0201313)

    # --- 9. Reglas de referencia -----------------------------------------
    obj("9 · el «silverman» de scipy cambia", "datos", ["m9", "distancias", "scipy"], 29.131313)
    obj("9 · bw.scott del plano cambia", "datos", ["m9", "plano", "scott_x"], 1213.1313)
    obj("9 · bw.nrd de faithful cambia", "datos", ["m9", "faithful", "nrd"], 0.3913131)

    # --- 10. Validación cruzada ------------------------------------------
    obj("10 · bw.SJ cambia", "datos", ["m10", "selectores", "SJ"], 0.1413131)
    obj("10 · la UCV deja de ver tres modas", "datos", ["m10", "modas", "ucv"], 2)
    obj("10 · el ruido de la rugosidad de la UCV cambia", "datos",
        ["m10", "aimse", ("selector", "ucv"), "ruido"], 71.313131)
    obj("10 · una moda del simulador cambia", "datos", ["m10", "curvas", "modas", 10], 4)
    obj("10 · la UCV con h = 0.001 deja de hundirse", "datos", ["m10", "empates", "ucv_001"], -0.3131313)
    obj("10 · la observación aislada cambia", "datos", ["m10", "aislada", 0, "x"], 3.1313)
    obj("10 · la curva LCV del simulador cambia", "datos", ["m10", "curvas", "lcv", 5], -0.9713131)

    # --- 11. EM, MISE de la mezcla y Monte Carlo -------------------------
    obj("11 · el EM da otra media", "datos", ["m11", "em", "mu", 1], 4.2713131)
    obj("11 · h* cambia", "datos", ["m11", "h_estrella"], 0.1313131)
    obj("11 · el sobrecoste de la UCV cambia", "datos",
        ["m11", "reales", ("selector", "ucv"), "sobre_pct"], 10.713131)
    obj("11 · la UCV gana otro % de veces", "datos",
        ["m11", "por_selector", ("selector", "ucv"), "gana_pct"], 41.3)
    obj("11 · la cola de la UCV (ISE > 2×SJ) cambia", "datos",
        ["m11", "por_selector", ("selector", "ucv"), "cola_pct"], 7.13)
    obj("11 · las réplicas con aviso de la UCV cambian", "datos",
        ["m11", "por_selector", ("selector", "ucv"), "avisos"], 7)
    obj("11 · la t emparejada UCV–SJ cambia", "datos", ["m11", "emparejadas", "ucv_sj", "t"], 11.313131)
    obj("11 · un ISE del JSON deja de ser el del CSV", "datos", ["m11", "ise", "SJ", 17], 0.0071313)
    obj("11 · el IC de la cola de la UCV cambia", "datos", ["m11", "cola_ucv_ic", 1], 6.713131)
    b, p = fila_csv("apendicea_mc.csv", 57, "ise_ucv", "0.0313131313")
    txt("11 · el CSV: un ISE de la UCV cambia", "mc", b, p, 0.0313131313)
    b, p = fila_csv("apendicea_mc.csv", 300, "aviso_bcv", "1")
    txt("11 · el CSV: la BCV avisa en una réplica", "mc", b, p)
    b, p = fila_csv("apendicea_mc.csv", 412, "h_SJ", "0.1713131313")
    txt("11 · el CSV: un h de SJ cambia", "mc", b, p, 0.1713131313)
    b, p = fila_csv("apendicea_mc_muestras.csv", 4, "y", "3.3131313131", ocurrencia=10)
    txt("11 · el CSV de muestras: un dato cambia", "muestras", b, p, 3.3131313131)

    # --- 12. Las sedes ---------------------------------------------------
    obj("12 · la fracción recíproca cambia", "datos", ["m12", "recipro", "pct"], 63.131313)
    obj("12 · los empates de todas las distancias cambian", "datos",
        ["m12", "selectores", "todas", "empates"], 3713)
    obj("12 · el umbral de empates cambia", "datos", ["m12", "umbral_empates"], 0.2913131)
    obj("12 · un dato en el borde deja de aportar ln 2", "datos",
        ["m12", "borde", "aporte", "aporte", 0], 0.7131313)
    obj("12 · Diggle deja de conservar la masa", "datos", ["m12", "borde", "masa_diggle"], 0.9813131)
    obj("12 · la masa con e(x) cambia", "datos", ["m12", "borde", "masa_e"], 0.9613131)
    obj("12 · los ceros dejan de ser 79", "datos", ["m12", "ceros"], 81)
    obj("12 · bw.ucv sin parejas ni ceros dice que avisa", "datos",
        ["m12", "selectores", "una_por_pareja_sin_ceros", "aviso"], True)
    obj("12 · la UCV exacta con 1 mm cambia de signo", "datos",
        ["m12", "selectores", "sin_ceros", "ucv_h_minusculo"], 0.0152031)
    obj("12 · Clark-Evans cambia", "datos", ["m12", "csr", "clark_evans"], 0.8313131)
    obj("12 · una distancia publicada cambia", "datos", ["m12", "nn", 100], 313.1)

    def permuta(d):
        u = d["m12"]["una_por_pareja"]
        i = next(k for k in range(len(u) - 1) if u[k] != u[k + 1])
        u[i], u[i + 1] = u[i + 1], u[i]
    fn("12 · «una por pareja» cambia de orden", "datos", permuta)

    # --- 13. Los ejercicios -----------------------------------------------
    obj("13 · un «pide» deja de estar en su enunciado", "soluciones",
        ["e4", "solucion", "respuestas", 0, "pide"],
        "Explica qué cambia al aumentar h y qué no cambia")
    obj("13 · un paso del ejercicio 7 cambia", "soluciones", ["e7", "pasos", 1, "valor"], 0.0913131)
    obj("13 · la fracción recíproca de Kennedy cambia", "soluciones",
        ["e10", "pasos", 2, "valor"], 57.131313)
    obj("13 · el menor k del ejercicio 8 cambia", "soluciones", ["e8", "pasos", 4, "valor"], 5)

    def respuesta_e1(s):
        r = s["e1"]["solucion"]["respuestas"][0]
        r["respuesta"] = r["respuesta"].replace("queda f̂(7) = 0.0717", "queda f̂(7) = 0.0731")
    fn("13 · una respuesta cambia su cifra", "soluciones", respuesta_e1)

    def demanda_huerfana(s):
        s["e2"]["enunciado"] += " Explica por qué el estimador no cuenta todas."
    fn("13 · un enunciado pide algo que nadie contesta", "soluciones", demanda_huerfana)
    obj("13 · los ejercicios dejan de ser diez", "soluciones", ["meta", "n_ejercicios"], 9)

    # --- Los mecanismos que la primera tanda dejó sin atacar ------------
    # La primera tanda (81) cazó todo y vio fallar 151 tipos de 499. Lo que
    # sigue no repite mecanismos: ataca código distinto del auditor —cada
    # ejercicio se recalcula por su camino—, el dpik que solo tiene la vía
    # sin agrupar, los avisos de las réplicas que se rehacen, la cota de la
    # simulación de CSR y el NaN.
    obj("1 · la barra de la media cuenta otra cosa", "datos", ["m1", "barra_media", "conteo"], 2)
    obj("2 · las modas mínimas de un ancho cambian", "datos", ["m2", "modas_min", 0], 7)
    obj("4 · una sede de la caja se mueve", "datos", ["m4", "plano", "x", 5], 1.3131)
    obj("4 · con V pequeña manda el sesgo", "datos", ["m4", "v_peq", "sesgo"], -0.1713131)
    obj("5 · la frontera |u| < 1 cambia", "datos", ["m5", "frontera", "lt"], 0.1313131)
    obj("6 · el gaussiano declara un soporte", "datos",
        ["m6", "nucleos", ("nombre", "gaussiano"), "soporte_por_sigma"], 3.1313131)
    obj("6 · la eficiencia del uniforme cambia", "datos",
        ["m6", "nucleos", ("nombre", "uniforme"), "eficiencia"], 0.9131313)
    obj("6 · el máximo de la unimodal cambia", "datos", ["m6", "unimodal", "max_gauss"], 0.1913131)
    obj("7 · Epanechnikov con la convención de R cambia", "datos",
        ["m7", "ingresos", "epa_density"], 0.0131313)
    obj("7 · las modas de hist(breaks = 30) cambian", "datos", ["m7", "mezcla", "hist_modas"], 6)
    obj("8 · el sesgo² en x = 0 cambia", "datos", ["m8", "sesgo2", 20], 0.0013131)
    obj("8 · el MISE mínimo es NaN", "datos", ["m8", "mise_min"], float("nan"))
    obj("9 · bw.nrd0 de las distancias cambia", "datos", ["m9", "distancias", "nrd0"], 19.131313)
    obj("10 · dpik cambia (solo tiene la vía sin agrupar)", "datos",
        ["m10", "selectores", "dpik"], 0.1813131)
    obj("10 · la LCV sin la aislada deja de moverse", "datos", ["m10", "h_lcv_sin"], 0.1013)
    obj("11 · la log-verosimilitud del EM cambia", "datos", ["m11", "em", "loglik"], -276.131313)
    obj("11 · el ISE mediano de SJ cambia", "datos",
        ["m11", "por_selector", ("selector", "SJ"), "ise_mediano"], 0.0081313)
    obj("11 · la diferencia BCV–SJ cambia", "datos", ["m11", "emparejadas", "bcv_sj", "media"], 0.00013131)
    b, p = fila_csv("apendicea_mc.csv", 5, "aviso_ucv", "1")
    txt("11 · el CSV: una réplica guardada avisa de más", "mc", b, p)
    obj("12 · la simulada de R se aleja de la fórmula", "datos", ["m12", "recipro", "csr_simulada"], 0.6513131)
    obj("12 · el h del borde cambia", "datos", ["m12", "borde", "h"], 21.313131)
    obj("12 · la curva de Diggle cambia", "datos", ["m12", "curvas", "diggle", 40], 0.0031313)
    obj("12 · la media bajo CSR cambia", "datos", ["m12", "csr", "media"], 213.13131)
    obj("12 · bw.SJ de una por pareja cambia", "datos",
        ["m12", "selectores", "una_por_pareja", "sj"], 21.313131)
    obj("12 · una cifra de «una por pareja» cambia", "datos", ["m12", "una_por_pareja", 200], 731.3)
    obj("13 · un paso del ejercicio 1 cambia", "soluciones", ["e1", "pasos", 6, "valor"], 4)
    obj("13 · un paso del ejercicio 3 cambia", "soluciones", ["e3", "pasos", 3, "valor"], 1.2713131313)
    obj("13 · un paso del ejercicio 4 cambia", "soluciones", ["e4", "pasos", 1, "valor"], 0.0813131313)
    obj("13 · un paso del ejercicio 5 cambia", "soluciones", ["e5", "pasos", 2, "valor"], 0.1313131313)
    obj("13 · un paso del ejercicio 6 cambia", "soluciones", ["e6", "pasos", 4, "valor"], 0.1131313131)
    obj("13 · un paso del ejercicio 9 cambia", "soluciones", ["e9", "pasos", 3, "valor"], 2)
    obj("13 · un bw.SJ de Kennedy cambia", "soluciones", ["e10", "pasos", 11, "valor"], 33.131313131)

    # --- Lo que añadió la revisión 2 (2026-10-02): una inyección por hallazgo
    obj("4 · el mejor V deja de bajar como n^(-1/5)", "datos", ["m4", "razon_v"], 1.5131313)
    obj("4 · la figura rellena otra sede", "datos", ["m4", "plano", "sitios", 0, "parzen_dentro", 0], 3)
    obj("5 · los tramos de modas pierden la etapa de dos", "datos", ["m5", "tramos", 2, "modas"], 3)
    obj("5 · la caja a la misma sd cambia", "datos", ["m5", "caja", "f_sd1"], 0.1813131)
    obj("6 · con el mismo soporte el triangular se aleja", "datos",
        ["m6", "mismo_soporte", "triangular", "dif_mismo_soporte"], 0.0313131)
    obj("7 · la ventana de los ingresos encierra tres", "datos", ["m7", "ingresos", "dentro"], 3)
    obj("8 · el mejor h puntual en x = 1 cambia", "datos", ["m8", "h_ecm_x", "h", 2], 0.6131313)
    obj("8 · sesgo² y varianza se cortan en el óptimo", "datos", ["m8", "cruce"], 0.3913131)
    obj("9 · el n en que se cruzan las reglas cambia", "datos", ["m9", "faithful", "n_cruce"], 6131.3131)
    obj("10 · el jitter se aleja de bw.ucv", "datos", ["m10", "empates", "jitter_max"], 0.1313131)
    obj("11 · los fallos de la UCV dejan de ser de anchos pequeños", "datos",
        ["m11", "cola_ucv", "h_max"], 0.1313131)
    obj("11 · la z de BCV–SJ cambia", "datos", ["m11", "dif_gana", "bcv_sj", "z"], 2.3131313)
    obj("12 · los ceros dejan de mandar en r = 0", "datos", ["m12", "borde", "f0_ceros"], 0.0003131)
    obj("12 · la UCV con 20 m cambia", "datos", ["m12", "selectores", "todas", "ucv_h20"], -0.0313131)
    obj("13 · el ejercicio 4 deja de acercarse al triangular", "soluciones",
        ["e4", "pasos", 3, "valor"], 0.0731313)
    obj("13 · el mínimo local más bajo de Kennedy cambia", "soluciones",
        ["e10", "pasos", 14, "valor"], 7.3131313)

    def sin_pista(s):
        del s["e5"]["pista"]
    fn("13 · un ejercicio pierde su pista", "soluciones", sin_pista)
    obj("14 · el generador dice que no comprobó anclas", "datos", ["meta", "anclas"], 0)

    # --- Los campos y los CSV que llegaron con la regeneración de las 14:59 --
    obj("0 · el diseño de la mezcla declara otra media", "datos", ["m7", "mezcla", "medias", 1], 9)
    obj("2 · la constante exacta de Scott cambia", "datos", ["m2", "scott", "constante_exacta"], 3.4313131)
    obj("6 · los datos para igualar del triangular cambian", "datos",
        ["m6", "nucleos", ("nombre", "triangular"), "datos_para_igualar"], 1.0313131)
    obj("6 · el Epanechnikov de R en x = 2 cambia", "datos", ["m6", "epa_bw1_en_2"], 0.0713131)
    b, p = linea_csv("apendicea_cafeteria.csv", 7, "tiempo", "4.1313131313")
    txt("13b · un tiempo del CSV de la cafetería cambia", "cafeteria", b, p, 4.1313131313)
    b, p = linea_csv("apendicea_faithful.csv", 20, "eruptions", "4.4313")
    txt("13b · una erupción del CSV de faithful cambia", "faithful", b, p, 4.4313)
    b, p = linea_csv("apendicea_faithful.csv", 40, "waiting", "97")
    txt("13b · una espera del CSV de faithful cambia", "faithful", b, p)
    b, p = linea_csv("apendicea_mezcla.csv", 50, "valor", "6.1313131313")
    txt("13b · un dato del CSV de la mezcla cambia", "mezcla", b, p, 6.1313131313)

    # --- 14. Formato -------------------------------------------------------
    txt("14 · una tilde se rompe en bytes crudos", "soluciones", "ó", "Ã³")
    obj("14 · un NA escrito como texto", "datos", ["m12", "borde", "f0_e"], "NA")
    obj("14 · un flotante con más de 8 decimales", "datos",
        ["m9", "faithful", "sd"], 1.14137125131313)
    obj("14 · la metainformación dice otro apéndice", "datos", ["meta", "apendice"], "B")

    return D


def _numeros(o, out):
    if isinstance(o, bool):
        return
    if isinstance(o, (int, float)):
        out.add(float(o))
    elif isinstance(o, dict):
        for v in o.values():
            _numeros(v, out)
    elif isinstance(o, list):
        for v in o:
            _numeros(v, out)


def valores_nuevos() -> list[str]:
    """Los defectos cuyo valor inyectado YA está en algún archivo."""
    hay: set[float] = set()
    for _, nombre in ARCHIVOS.values():
        p = SALIDAS / nombre
        if nombre.endswith(".json"):
            _numeros(json.loads(p.read_text(encoding="utf-8")), hay)
        else:
            for linea in p.read_text(encoding="utf-8").splitlines()[1:]:
                for c in linea.split(","):
                    try:
                        hay.add(float(c))
                    except ValueError:
                        pass
    malos = []
    for nombre, v in INYECTADOS:
        vs = v if isinstance(v, list) else [v]
        for x in vs:
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                continue
            if float(x).is_integer() and abs(x) < 100:
                continue                 # un conteo pequeño siempre coincide con otro
            if float(x) in hay:
                malos.append(f"{nombre}: {x}")
    return malos


def tipo_de(nombre: str) -> str:
    """Colapsa las instancias de un mismo mecanismo en un solo nombre.

    El apéndice repite la misma pregunta sobre seis núcleos, siete
    selectores, cinco selectores del Monte Carlo, cuatro subconjuntos de
    distancias y diez ejercicios: atacar «biweight, R(K)» prueba lo mismo
    que atacar «triweight, R(K)», que el auditor integra el núcleo.
    """
    reglas = [
        (r"^m3: distancia al triangular, m=\d+$", "m3: la distancia al triangular"),
        (r"^m3: (cortes|conteos) del corrimiento \d$", r"m3: \1 de un corrimiento"),
        (r"^m3: el corrimiento \d cuenta los 8$", "m3: un corrimiento cuenta los 8"),
        (r"^m3: área del ASH, m=\d+$", "m3: el área del ASH"),
        (r"^m4: n = \d+, (.+)$", r"m4: por n, \1"),
        (r"^m4: (v_peq|v_gra|v_min), (.+)$", r"m4: una ventana, \2"),
        (r"^m4: sitio (denso|medio|ralo), (.+)$", r"m4: un sitio, \2"),
        (r"^m5: tabla, (uniforme|gaussiano) con h=.+$", r"m5: tabla, \1"),
        (r"^m6: (gaussiano|epanechnikov|uniforme|triangular|biweight|triweight), (.+)$",
         r"m6: un núcleo, \2"),
        (r"^m6: density\(\) y 1/√μ₂: .+$", "m6: density() y 1/√μ₂"),
        (r"^m6: en el plano, h²/σ² del .+$", "m6: en el plano, h²/σ²"),
        (r"^m6: y vale \d \(.+\)$", "m6: en el plano, el valor de la literatura"),
        (r"^m6: (trimodal|unimodal), (.+)$", r"m6: una muestra, \2"),
        (r"^m7: área del k-NN en .+$", "m7: un área del k-NN"),
        (r"^m7: mezcla, (modas|área|el valle|el máximo) con k=\d+$", r"m7: mezcla, \1 con k"),
        (r"^m10: modas con .+$", "m10: las modas con un selector"),
        (r"^m10: (el h|rugosidad|el ruido R\(K''\)/\(nh⁵\)) de \w+( \(.+\))?$", r"m10: \1\2"),
        (r"^m10: aislada, h=[\d.]+: (.+)$", r"m10: aislada, \1"),
        (r"^m11: real, (.+) de \w+$", r"m11: real, \1"),
        (r"^mc: (nrd0|nrd|ucv|bcv|SJ), (.+)$", r"mc: un selector, \2"),
        (r"^mc: (ucv_sj|bcv_sj), (.+)$", r"mc: una emparejada, \2"),
        (r"^m12: (todas|sin ceros|una/pareja|una/pareja sin 0), (.+)$", r"m12: un subconjunto, \2"),
        (r"^m12: (todas|sin_ceros|una_por_pareja): (.+)$", r"m12: con empates, \2"),
        (r"^e\d+: (trae respuestas, y ninguna vacía|cada «pide» está literal en su enunciado|"
         r"ninguna demanda se queda sin respuesta|trae su lectura)$", r"ej: \1"),
        (r"^ej: está e\d+$", "ej: está cada ejercicio"),
        (r"^semilla: .+$", "semilla: las mismas z"),
        (r"^fmt: (datos|soluciones), (.+)$", r"fmt: \2"),
    ]
    for pat, destino in reglas:
        if re.match(pat, nombre):
            return re.sub(pat, destino, nombre)
    return nombre


# Las comprobaciones que este arnés NO PUEDE romper, y no es una laguna: no
# leen los archivos que él envenena. Contrastan las fuentes primarias (las
# sedes del capítulo 5, el gpkg) o la propia maquinaria del auditor.
INATACABLES = frozenset({
    "sedes: 2 107 urbanas (las del capítulo 5)",
    "sedes: 262 de Kennedy (las del capítulo 5)",
    "área urbana: el gpkg, releído (km²)",
    "área urbana: la del capítulo 5",
    "m1: el área del histograma es 1",
    "m3: y la función ash() da lo mismo",
    "m4: los tres sitios son distintos",
    "m10: ni bw.ucv ni bw.bcv avisan",
    "m12: la cuadratura da ln 2 en el borde",
    "m12: y la simulada aquí, con numpy",
    "m12: una por pareja: n − parejas",
    "e4: el hueco de 3.5 se rellena al subir m",
    "e6: la curva contra k no es monótona",
    "e10: sin aviso, sin mínimo; sin empates, junto a SJ",
    "fmt: y hay tildes que comprobar",
})


if __name__ == "__main__":
    lista = defectos()
    repetidos = valores_nuevos()
    if repetidos:
        print("PARADO: estos valores inyectados ya están en los archivos, y un acierto")
        print("podría serlo por el motivo equivocado:")
        for r in repetidos:
            print(f"   · {r}")
        raise SystemExit(1)
    print(f"  {len(INYECTADOS)} valores inyectados, ninguno presente ya en los archivos")
    raise SystemExit(arnes(
        "prueba_auditor_apendicea.py — el arnés del auditor del apéndice A",
        PY, AUDITOR, SALIDAS, ARCHIVOS, lista,
        "precalculo/rscript.sh precalculo/genera_apendicea.R",
        agrupa=tipo_de, inatacables=INATACABLES))
