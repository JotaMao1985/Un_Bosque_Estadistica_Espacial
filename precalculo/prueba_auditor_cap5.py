#!/usr/bin/env python3
"""
prueba_auditor_cap5.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T3.4b.

POR QUÉ EXISTE. Un auditor que informa «0 fallos» la primera vez no ha
demostrado nada: puede estar comprobando bien o puede estar comprobando
cosas incapaces de fallar. `audita_cap5.py` dio 196/0 en su primera pasada
limpia —después de cazar cinco defectos reales, tres de ellos de la misma
familia—, y sin este arnés esa cifra sería una promesa.

La maquinaria vive en `prueba_auditor_base.py`. Aquí solo se declara QUÉ
romper, que es lo único propio del capítulo.

LAS FAMILIAS DE DEFECTO, y cada una imita algo que ya pasó o que este
capítulo puede sufrir:

   1. cifra publicada que deja de cuadrar con la fuente primaria
   2. cifra derivada que deja de cuadrar con las que la generan
   3. relación cualitativa que se rompe (órdenes, monotonías, signos)
   4. LA INVERSIÓN DE `relrisk`                        ← el defecto REAL de
      este capítulo: el mapa publicaba P(privado) con el título, la
      mediana y la conclusión de P(oficial), y todo daba verde
   5. la clave del deslizador escrita con dos precisiones ← el otro defecto
      real: el mismo sigma salía `233.39486671` en los mapas y
      `233.3948667117` en los datos, y el `find()` habría fallado callado
   6. la escala común de la familia, rota en una superficie
   7. propiedad TEÓRICA exacta violada (2/(nsim+1), mu/(1-alpha/beta))
   8. una cifra que se puede recalcular desde su CSV        ← el Hawkes
   9. bandera que deja de coincidir con el hecho que afirma
  10. caja, cuantización o contenido de un `.geomapa`
  11. tilde convertida en bytes crudos
  12. flotante con más decimales de los declarados
  13. solución de un ejercicio guiado alterada
  14. coherencia entre módulos rota

UNA INYECCIÓN NO PUEDE USAR UN VALOR QUE YA ESTÉ EN EL ARCHIVO. Si la
cifra falsa coincidiera con otra real, el auditor podría «cazarla» por el
motivo equivocado y el arnés se felicitaría solo. De ahí los valores con
pinta de matrícula.

Uso:  python3 precalculo/prueba_auditor_cap5.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prueba_auditor_base import arnes

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_cap5.py"

ARCHIVOS = {
    "datos": ("CAP5_DATOS", "cap5_datos.json"),
    "mapas": ("CAP5_MAPAS", "cap5_mapas.json"),
    "soluciones": ("CAP5_SOLUCIONES", "cap5_soluciones.json"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


def defectos():
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D = []

    def obj(nombre, clave, fn):
        D.append((nombre, clave, "obj", fn))

    def txt(nombre, clave, busca, pone):
        D.append((nombre, clave, "txt", (busca, pone)))

    # --- 1. Contra la fuente primaria ---------------------------------
    obj("1 · las sedes de Kennedy cambian",
        "datos", lambda d: d["m1"]["ventana"].__setitem__("n", 271))
    obj("1 · el área de Kennedy cambia",
        "datos", lambda d: d["m1"]["ventana"].__setitem__("area_km2", 41.3131313131))
    obj("1 · el conteo por atributo de Kennedy cambia",
        "datos", lambda d: d["m1"]["frontera"].__setitem__("n_atributo", 253))
    obj("1 · las sedes que discrepan dejan de ser tres",
        "datos", lambda d: d["m1"]["frontera"].__setitem__("n_discrepan", 5))
    obj("1 · la distancia al borde de la más lejana cambia",
        "datos", lambda d: d["m1"]["frontera"].__setitem__("dist_max_m", 171.7171717171))
    obj("1 · las sedes oficiales cambian",
        "datos", lambda d: d["m6"]["bogota"].__setitem__("oficiales", 731))
    obj("1 · las sedes privadas cambian",
        "datos", lambda d: d["m6"]["bogota"].__setitem__("privadas", 1417))
    obj("1 · las sedes con grado 11 cambian",
        "datos", lambda d: d["m5"]["capas"]["grado_11"].__setitem__("n", 1131))
    obj("1 · los evaluados de Saber 11 cambian",
        "datos", lambda d: d["m5"]["capas"]["estudiantes"].__setitem__("total", 147131))
    obj("1 · los casos de laringe de chorley cambian",
        "datos", lambda d: d["m6"]["chorley"].__setitem__("casos", 61))
    obj("1 · los eventos simulados del Hawkes cambian",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("n_eventos", 4717))

    # --- 2. Cifras derivadas ------------------------------------------
    obj("2 · lambda de Kennedy deja de ser n entre el área",
        "datos", lambda d: d["m1"]["ventana"].__setitem__("lambda_km2", 7.1717171717))
    obj("2 · la celda declarada deja de salir de la caja",
        "datos", lambda d: d["m2"]["familia"].__setitem__("celda_m", 71.7171717171))
    obj("2 · la caída total de la familia cambia",
        "datos", lambda d: d["m2"]["familia"].__setitem__("caida_pct", 41.3131313131))
    obj("2 · la horquilla del borde deja de cuadrar",
        "datos", lambda d: d["m4"].__setitem__("horquilla_pct", 31.3131313131))
    obj("2 · la razón entre selectores de Kennedy cambia",
        "datos", lambda d: d["m3"]["kennedy"].__setitem__("razon", 3.1313131313))
    obj("2 · la proporción global de oficiales cambia",
        "datos", lambda d: d["m6"]["bogota"].__setitem__("prop_global", 0.4131313131))
    obj("2 · la brecha entre la mediana y la global cambia",
        "datos", lambda d: d["m6"]["bogota"].__setitem__(
            "brecha_mediana_menos_global", -0.1717171717))
    obj("2 · el porcentaje de sedes con grado 11 cambia",
        "datos", lambda d: d["m5"]["capas"]["grado_11"].__setitem__(
            "pct_de_las_sedes", 41.3131313131))
    obj("2 · cuánto infla la cola en bei deja de ser el cociente",
        "datos", lambda d: d["m7"]["bei"]["elevacion"].__setitem__("cola_infla", 3.13131))
    obj("2 · la razón total de la curva de Bogotá cambia",
        "datos", lambda d: d["m7"]["bogota"]["curva"].__setitem__("razon", 17.1717))
    obj("2 · el sigma mínimo dibujable deja de ser tres celdas",
        "datos", lambda d: d["m5"]["rejilla"].__setitem__(
            "sigma_minimo_dibujable_m", 313.1313131313))
    obj("2 · la EMV homogénea deja de ser n entre el área",
        "datos", lambda d: d["m8"]["homogeneo"].__setitem__("lambda_mle_m2", 6.13131e-06))
    obj("2 · lambda en km² deja de ser la de m² por un millón",
        "datos", lambda d: d["m8"]["homogeneo"].__setitem__("lambda_km2", 6.1313131313))
    obj("2 · el movimiento del AIC con la cuadratura cambia",
        "datos", lambda d: d["m8"]["cuadratura"].__setitem__("rango_aic", 31.3131313131))
    obj("2 · la mejora del condicionamiento al centrar cambia",
        "datos", lambda d: d["m9"].__setitem__("mejora_condicion", 1717.17))
    obj("2 · la divergencia en mu del Thomas cambia",
        "datos", lambda d: d["m11"]["divergencia"][0].__setitem__("mu_pct", 13.1313131313))
    obj("2 · los repetidos dejan de ser la resta de los dos n",
        "datos", lambda d: d["m11"]["duplicados"].__setitem__("repetidos", 47))
    obj("2 · la razón de ramificación deja de ser alpha/beta",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("razon_ramificacion", 0.4131313131))
    obj("2 · la tasa teórica del Hawkes cambia",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("tasa_teorica", 1.7171717171))
    obj("2 · la tasa simulada deja de ser eventos entre T",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("tasa_simulada", 1.3131313131))

    # --- 3. Relaciones cualitativas -----------------------------------
    obj("3 · el máximo de la familia deja de caer al abrir",
        "datos", lambda d: d["m2"]["familia"]["max_km2"].__setitem__(3, 99.1313131313))
    obj("3 · la fuga sin corregir se vuelve positiva",
        "datos", lambda d: d["m4"]["tabla"][1].__setitem__("fuga_sin_corregir_pct", 1.7171717171))
    obj("3 · el exceso del defecto se vuelve negativo",
        "datos", lambda d: d["m4"]["tabla"][1].__setitem__("exceso_defecto_pct", -1.7171717171))
    obj("3 · las desviaciones de borde dejan de crecer",
        "datos", lambda d: d["m4"]["tabla"][2].__setitem__("exceso_defecto_pct", 0.1313131313))
    obj("3 · los selectores discrepan más en Kennedy que en la ciudad",
        "datos", lambda d: d["m3"]["urbana"].__setitem__("razon", 1.1313131313))
    obj("3 · el orden de las tres covariables en el bulto se rompe",
        "datos", lambda d: d["m7"]["bogota"]["curva"].__setitem__("razon_bulto", 9.1313131313))
    obj("3 · la cola pasa a encoger en vez de inflar",
        "datos", lambda d: d["m7"]["bei"]["pendiente"].__setitem__("cola_infla", 0.4131313131))
    obj("3 · más nd deja de dar más puntos ficticios",
        "datos", lambda d: d["m8"]["cuadratura"]["tabla"][3].__setitem__("ficticios", 313))
    obj("3 · la isotrópica pasa a costar menos que la traslación",
        "datos", lambda d: d["m11"]["ajustes"][0].__setitem__("segundos", 0.0131313131))
    obj("3 · el Hawkes deja de salir más agregado que su Poisson",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("dispersion_hawkes", 0.4131313131))
    obj("3 · el patrón deja de salirse de la banda del modelo",
        "datos", lambda d: d["m10"].__setitem__("pct_r_fuera_de_banda", 0.0))
    obj("3 · la banda de la envolvente se cruza",
        "datos", lambda d: d["m10"]["curva"]["hi"].__setitem__(40, -1.7171717171))
    obj("3 · la rejilla de r deja de ser creciente",
        "datos", lambda d: d["m10"]["curva"]["r"].__setitem__(40, 17.1717171717))
    obj("3 · los duplicados pasan a descuadrar el ajuste",
        "datos", lambda d: d["m11"]["duplicados"].__setitem__("cambio_maximo_pct", 41.3131))
    obj("3 · las dos correcciones dejan de divergir",
        "datos", lambda d: [x.__setitem__("mu_pct", 1.3131313131)
                            for x in d["m11"]["divergencia"]])
    obj("3 · la celda deja de caber tres veces en el sigma menor",
        "datos", lambda d: d["m2"]["familia"]["sigmas_m"].__setitem__(0, 91.3131))

    # --- 4. LA INVERSIÓN DE relrisk, el defecto real del capítulo -----
    obj("4 · el mapa vuelve a publicar P(privado) como si fuera P(oficial)",
        "datos", lambda d: d["m6"]["bogota"].__setitem__(
            "p_mediana", 1 - d["m6"]["bogota"]["p_mediana"]))
    obj("4 · el ráster de proporción se invierte",
        "mapas", lambda m: m["proporcion_oficial"].__setitem__(
            "zq", [z if z < 0 else m["proporcion_oficial"]["zqmax"] - z
                   for z in m["proporcion_oficial"]["zq"]]))
    obj("4 · la orientación verificada baja de la proporción global",
        "datos", lambda d: d["m6"]["bogota"].__setitem__("orientacion_verificada", 0.1313131313))
    obj("4 · y la de chorley, lo mismo",
        "datos", lambda d: d["m6"]["chorley"].__setitem__("orientacion_verificada", 0.0131313131))
    obj("4 · el veredicto de concentración deja de cuadrar con su cifra",
        "datos", lambda d: d["m6"]["bogota"].__setitem__("concentrado", False))

    # --- 5. La clave del deslizador, el otro defecto real -------------
    obj("5 · el sigma del mapa deja de coincidir con el del dato",
        "mapas", lambda m: m["kennedy_familia"][2].__setitem__(
            "sigma_m", m["kennedy_familia"][2]["sigma_m"] + 1e-6))
    obj("5 · las superficies se publican en otro orden",
        "mapas", lambda m: m.__setitem__(
            "kennedy_familia", list(reversed(m["kennedy_familia"]))))

    # --- 6. La escala común -------------------------------------------
    obj("6 · una superficie de la familia usa otra escala",
        "mapas", lambda m: m["kennedy_familia"][3].__setitem__(
            "escala_comun", [0.0131313131, 0.4131313131]))
    obj("6 · el máximo cuantizado deja de caer entre superficies",
        "mapas", lambda m: m["kennedy_familia"][4]["zq"].__setitem__(0, 1000))
    obj("6 · la caída del máximo cuantizado se vuelve invisible",
        "mapas", lambda m: [g["zq"].__setitem__(0, 1000) for g in m["kennedy_familia"]])

    # --- 7. Propiedades teóricas exactas ------------------------------
    obj("7 · el nivel puntual deja de ser 2/(nsim+1)",
        "datos", lambda d: d["m10"].__setitem__("nivel_puntual_pct", 0.4131313131))
    obj("7 · la simulación del Hawkes deja de cuadrar con la teoría",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("tasa_teorica",
                                                          d["m11"]["hawkes"]["tasa_simulada"] * 1.4))

    # --- 8. Lo que se recalcula desde su CSV --------------------------
    obj("8 · el índice de dispersión del Hawkes cambia",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("dispersion_hawkes", 7.1717171717))
    obj("8 · y el de su Poisson",
        "datos", lambda d: d["m11"]["hawkes"].__setitem__("dispersion_poisson", 3.1313131313))
    obj("8 · el máximo de la familia deja de cuadrar con la KDE",
        "datos", lambda d: d["m2"]["familia"]["max_km2"].__setitem__(0, 41.3131313131))
    obj("8 · el exceso del defecto deja de cuadrar con la KDE",
        "datos", lambda d: d["m4"]["tabla"][0].__setitem__("exceso_defecto_pct", 4.1313131313))
    obj("8 · el percentil 5 del bulto deja de salir de la covariable",
        "datos", lambda d: d["m7"]["bogota"]["curva"].__setitem__("bulto_desde", 1313.13))

    # --- 9. Banderas que dejan de coincidir con su hecho --------------
    obj("9 · el ppm crudo deja de declararse singular",
        "datos", lambda d: d["m9"]["crudo"].__setitem__("singular", False))
    obj("9 · el ppm centrado se declara singular",
        "datos", lambda d: d["m9"]["centrado"].__setitem__("singular", True))
    obj("9 · el selector que chocó deja de declararlo",
        "datos", lambda d: d["m3"]["topes"][0].__setitem__("choco", False))
    obj("9 · el defecto de la cuadratura deja de ser nd = 100",
        "datos", lambda d: d["m8"]["cuadratura"].__setitem__("defecto_ficticios", 1313))
    obj("9 · la corrección de la envolvente cambia de nombre",
        "datos", lambda d: d["m10"].__setitem__("correccion", "isotropic"))
    obj("9 · el caso de Demirel aparece relleno sin su fuente",
        "datos", lambda d: d["m5"].__setitem__("caso_demirel", {"cifra": 13.13}))
    obj("9 · un selector descartado por resolución sí llegaba",
        "datos", lambda d: d["m5"]["rejilla"].__setitem__(
            "selectores_descartados", ["diggle", "ppl", "CvL"]))

    # --- 10. El .geomapa ----------------------------------------------
    obj("10 · la caja de un mapa de puntos se desordena",
        "mapas", lambda m: m["kennedy_puntos"].__setitem__(
            "caja", [9e6, 9e6, 1.0, 1.0]))
    obj("10 · la cuantización de un mapa de puntos miente",
        "mapas", lambda m: m["kennedy_puntos"].__setitem__("q", 3131))
    obj("10 · un ráster pierde celdas",
        "mapas", lambda m: m["ciudad_oferta"].__setitem__(
            "zq", m["ciudad_oferta"]["zq"][:-13]))
    obj("10 · un ráster deja de marcar las celdas de fuera",
        "mapas", lambda m: m["ciudad_oferta"].__setitem__(
            "zq", [0 if z < 0 else z for z in m["ciudad_oferta"]["zq"]]))
    obj("10 · un ráster se sale de su propia cuantización",
        "mapas", lambda m: m["ciudad_estudiantes"]["zq"].__setitem__(500, 31313))
    obj("10 · un mapa cambia de modo",
        "mapas", lambda m: m["ciudad_oferta"].__setitem__("modo", "puntos"))
    obj("10 · falta una superficie de la familia",
        "mapas", lambda m: m.__setitem__(
            "kennedy_familia", m["kennedy_familia"][:-1]))

    # --- 11 y 12. Tildes y decimales ----------------------------------
    txt("11 · una tilde se convierte en bytes crudos",
        "datos", "proporción", "proporciÃ³n")
    obj("12 · un flotante se publica con más decimales de los declarados",
        "datos", lambda d: d["m1"]["ventana"].__setitem__(
            "area_km2", 38.512345678901234))
    obj("12 · un NaN se cuela en la curva de la envolvente",
        "datos", lambda d: d["m10"]["curva"]["obs"].__setitem__(50, float("nan")))

    # --- 13. Los ejercicios -------------------------------------------
    obj("13 · el ejercicio 1 deja de tener un selector que chocó",
        "soluciones", lambda s: s["e1"]["solucion"].__setitem__("n_chocaron", 0))
    obj("13 · en el ejercicio 2 Diggle deja de estar más cerca",
        "soluciones", lambda s: s["e2"]["solucion"]["tabla"][1].__setitem__(
            "diggle_pct", 1.7171717171))
    obj("13 · en el ejercicio 3 la cola deja de inflar",
        "soluciones", lambda s: s["e3"]["solucion"].__setitem__("cola_infla", 0.4131313131))
    obj("13 · en el ejercicio 4 desplazar mueve las pendientes",
        "soluciones", lambda s: s["e4"]["solucion"].__setitem__(
            "dif_relativa_pendientes", 0.1717171717))
    obj("13 · en el ejercicio 5 las correcciones dejan de divergir",
        "soluciones", lambda s: s["e5"]["solucion"]["diferencias_pct"].__setitem__(
            "kappa", 0.1313131313) or s["e5"]["solucion"]["diferencias_pct"].__setitem__(
            "escala", 0.1313131313) or s["e5"]["solucion"]["diferencias_pct"].__setitem__(
            "mu", 0.1313131313))
    obj("13 · un ejercicio se queda sin enunciado",
        "soluciones", lambda s: s["e3"].__setitem__("enunciado", "   "))
    obj("13 · un ejercicio se queda sin pasos",
        "soluciones", lambda s: s["e2"].__setitem__("pasos", s["e2"]["pasos"][:2]))
    obj("13 · los ejercicios dejan de ser cinco",
        "soluciones", lambda s: s["meta"].__setitem__("n_ejercicios", 4))

    # --- 14. Coherencia entre módulos ---------------------------------
    obj("14 · los duplicados dicen cosas distintas en dos sitios",
        "datos", lambda d: d["meta"]["duplicados"].__setitem__("repetidos", 47))
    obj("14 · la metainformación cambia de capítulo",
        "datos", lambda d: d["meta"].__setitem__("capitulo", 4))
    obj("14 · el capítulo cambia de semanas",
        "datos", lambda d: d["meta"].__setitem__("semanas", "8-9"))
    obj("14 · dos semillas del capítulo se repiten",
        "datos", lambda d: d["meta"]["semillas"].__setitem__("simulacion", 5028))
    obj("14 · una semilla repite la global",
        "datos", lambda d: d["meta"]["semillas"].__setitem__("hawkes", 2026))
    obj("14 · el conteo de anclas se desploma",
        "datos", lambda d: d["meta"].__setitem__("n_anclas", 3))
    obj("14 · el CSV de la familia y el JSON dejan de coincidir",
        "datos", lambda d: d["m2"]["familia"]["max_km2"].__setitem__(0, 29.5131313131))
    obj("14 · el mapa de ciudad deja de usar el dibujable más estrecho",
        "datos", lambda d: d["m5"].__setitem__("sigma_m", 1251.3131313131))
    obj("14 · los selectores de Kennedy dejan de ser los de sus sedes",
        "datos", lambda d: d["m3"]["kennedy"].__setitem__("n", 271))

    # --- 15. Mecanismos que la primera tanda dejó sin ver fallar ------
    # El arnés imprime qué comprobaciones no se han visto fallar, y la
    # primera tanda dejó 185. La mayoría son OTRAS INSTANCIAS de lo mismo
    # —las diez comprobaciones del núcleo repetidas en doce mapas— pero
    # entre ellas había MECANISMOS enteros sin tocar, y uno importa: la
    # reimplementación de `bw.scott` con su fórmula cerrada, que es la
    # única de los cuatro selectores que este auditor puede recalcular.
    obj("15 · bw.scott deja de salir de su fórmula cerrada",
        "datos", lambda d: d["m3"]["kennedy"]["sigmas_m"].__setitem__("scott", 613.1313131313))
    obj("15 · un selector se vuelve negativo",
        "datos", lambda d: d["m3"]["urbana"]["sigmas_m"].__setitem__("CvL", -717.17))
    obj("15 · los casos de tope dejan de ser dos",
        "datos", lambda d: d["m3"].__setitem__("topes", d["m3"]["topes"][:1]))
    obj("15 · el valor de un selector que chocó se anula",
        "datos", lambda d: d["m3"]["topes"][1].__setitem__("sigma", 0.0))
    obj("15 · los nodos de la envolvente dejan de ser los que declara",
        "datos", lambda d: d["m10"].__setitem__("n_nodos", 131))
    obj("15 · el primer r fuera de banda cambia",
        "datos", lambda d: d["m10"].__setitem__("primer_r_fuera_m", 1313.13))
    obj("15 · la oferta deja de ser todas las sedes",
        "datos", lambda d: d["m5"]["capas"]["oferta"].__setitem__("n", 2113))
    obj("15 · oferta y estudiantes pasan a ser el mismo mapa",
        "datos", lambda d: d["m5"].__setitem__("cor_oferta_estudiantes", 0.9993131313))
    obj("15 · los ajustes de kppm dejan de ser seis",
        "datos", lambda d: d["m11"].__setitem__("ajustes", d["m11"]["ajustes"][:4]))
    obj("15 · la rejilla de un ráster declara un lado imposible",
        "mapas", lambda m: m["ciudad_oferta"].__setitem__("nx", 0))
    obj("15 · un ráster se queda sin cuantización declarada",
        "mapas", lambda m: m["proporcion_oficial"].__setitem__("zqmax", 0))
    obj("15 · un ráster mete un negativo que no es la máscara",
        "mapas", lambda m: m["ciudad_estudiantes"]["zq"].__setitem__(700, -13))
    obj("15 · la caja de un ráster se desordena",
        "mapas", lambda m: m["proporcion_oficial"].__setitem__(
            "caja", [9e6, 9e6, 1.0, 1.0]))
    obj("15 · una superficie de la familia pierde celdas",
        "mapas", lambda m: m["kennedy_familia"][5].__setitem__(
            "zq", m["kennedy_familia"][5]["zq"][:-7]))
    obj("15 · una superficie de la familia se desordena la caja",
        "mapas", lambda m: m["kennedy_familia"][1].__setitem__(
            "caja", [9e6, 9e6, 1.0, 1.0]))
    obj("15 · una superficie declara una q que no es válida",
        "mapas", lambda m: m["kennedy_familia"][2].__setitem__("q", 3131))
    obj("15 · un ejercicio desaparece del JSON",
        "soluciones", lambda s2: s2.pop("e4", None))

    # --- 16. Los 37 tipos que el recuento por TIPOS dejó ver ----------
    # Esta tanda no se escribió a ojo: sale de la lista que el arnés
    # imprime al final. Antes de subir el recuento por tipos al núcleo, el
    # informe decía «165 sin ver fallar» y esa cifra no se podía trabajar
    # —la mayoría eran instancias de lo mismo—. Con los tipos separados
    # quedaban 37 mecanismos concretos, y esto es uno por cada uno.
    obj("16 · un mapa de puntos cambia de modo",
        "mapas", lambda m: m["kennedy_puntos"].__setitem__("modo", "grafo"))
    obj("16 · un mapa de puntos declara un modo que no existe",
        "mapas", lambda m: m["sector_puntos"].__setitem__("modo", "calor"))
    obj("16 · un ráster declara un modo que no existe",
        "mapas", lambda m: m["ciudad_estudiantes"].__setitem__("modo", "calor"))
    obj("16 · un mapa de puntos declara una codificación inventada",
        "mapas", lambda m: m["kennedy_puntos"].__setitem__("codificacion", "zigzag"))
    obj("16 · un ráster declara una codificación inventada",
        "mapas", lambda m: m["ciudad_oferta"].__setitem__("codificacion", "zigzag"))
    obj("16 · una superficie de la familia declara otra codificación",
        "mapas", lambda m: m["kennedy_familia"][0].__setitem__("codificacion", "zigzag"))
    obj("16 · un ráster declara una q inválida",
        "mapas", lambda m: m["ciudad_oferta"].__setitem__("q", 999))
    obj("16 · la q de un mapa de puntos queda inflada",
        "mapas", lambda m: m["kennedy_puntos"].__setitem__(
            "pts", [v // 8 for v in m["kennedy_puntos"]["pts"]]))
    obj("16 · un mapa de puntos se hincha por encima de su presupuesto",
        "mapas", lambda m: m["kennedy_puntos"].__setitem__(
            "pts", m["kennedy_puntos"]["pts"] * 900))
    obj("16 · un ráster se hincha por encima de su presupuesto",
        "mapas", lambda m: m["proporcion_oficial"].__setitem__(
            "cortes", [0.13131 + i for i in range(90000)]))
    obj("16 · una superficie de la familia se hincha",
        "mapas", lambda m: m["kennedy_familia"][0].__setitem__(
            "cortes", [0.13131 + i for i in range(90000)]))
    obj("16 · una superficie de la familia pierde su cuantización",
        "mapas", lambda m: m["kennedy_familia"][1].__setitem__("zqmax", None))
    obj("16 · una superficie de la familia pierde un lado",
        "mapas", lambda m: m["kennedy_familia"][2].__setitem__("ny", None))
    obj("16 · una superficie de la familia se sale de su cuantización",
        "mapas", lambda m: m["kennedy_familia"][3]["zq"].__setitem__(300, 31313))
    obj("16 · una superficie de la familia mete un negativo que no es máscara",
        "mapas", lambda m: m["kennedy_familia"][4]["zq"].__setitem__(300, -13))
    for nm in ("ciudad_oferta", "ciudad_estudiantes", "proporcion_oficial",
               "kennedy_puntos", "sector_puntos"):
        obj(f"16 · falta el mapa `{nm}`",
            "mapas", (lambda n: (lambda m: m.pop(n, None)))(nm))
    obj("16 · un NaN se cuela en los mapas",
        "mapas", lambda m: m["ciudad_oferta"]["cortes"].__setitem__(0, float("nan")))
    obj("16 · un NaN se cuela en las soluciones",
        "soluciones", lambda s: s["e3"]["solucion"].__setitem__("razon_bulto", float("nan")))
    obj("16 · Kennedy: el conteo geométrico deja de ser el suyo",
        "datos", lambda d: d["m1"]["frontera"].__setitem__("n_geometria", 271))
    obj("16 · el error de Diggle deja de estar cien veces más cerca",
        "datos", lambda d: d["m4"]["tabla"][0].__setitem__("error_diggle_pct", 0.4131313131))
    obj("16 · la familia deja de tener siete sigmas",
        "datos", lambda d: d["m2"]["familia"].__setitem__(
            "sigmas_m", d["m2"]["familia"]["sigmas_m"][:5]))
    obj("16 · la EMV deja de coincidir a precisión de máquina",
        "datos", lambda d: d["m8"]["homogeneo"].__setitem__("dif_relativa", 0.0131313131))
    obj("16 · centrar deja de mejorar el condicionamiento",
        "datos", lambda d: d["m9"]["centrado"].__setitem__("cond_reciproco", 1.31e-13))
    obj("16 · el AIC se mueve menos que un parámetro de más",
        "datos", lambda d: d["m8"]["cuadratura"].__setitem__("rango_aic", 0.1313131313))
    obj("16 · el ppm centrado pierde un error estándar",
        "datos", lambda d: d["m9"]["centrado"].__setitem__(
            "ee", d["m9"]["centrado"]["ee"][:1]))
    obj("16 · el ppm crudo pasa a publicar errores estándar",
        "datos", lambda d: d["m9"]["crudo"].__setitem__("ee", [0.13, 0.13, 0.13]))
    obj("16 · el movimiento de la pendiente en errores estándar cambia",
        "datos", lambda d: d["m8"]["cuadratura"].__setitem__(
            "rango_pendiente_en_ee", 3.1313131313))
    obj("16 · el percentil 95 del bulto deja de salir de la covariable",
        "datos", lambda d: d["m7"]["bogota"]["curva"].__setitem__("bulto_hasta", 13131.3))
    obj("16 · un selector de Kennedy se vuelve negativo",
        "datos", lambda d: d["m3"]["kennedy"]["sigmas_m"].__setitem__("ppl", -374.13))
    obj("16 · el segundo caso de tope deja de declararse",
        "datos", lambda d: d["m3"]["topes"][1].__setitem__("choco", False))
    obj("16 · falta la familia entera del deslizador",
        "mapas", lambda m: m.pop("kennedy_familia", None))
    obj("16 · una superficie de la familia declara un modo que no existe",
        "mapas", lambda m: m["kennedy_familia"][6].__setitem__("modo", "calor"))

    return D


def tipo(n: str) -> str:
    """Colapsa las instancias de un mismo mecanismo en un solo nombre.

    El núcleo pone DIEZ comprobaciones por mapa y este capítulo publica
    DOCE mapas —siete de ellos la misma familia con otro sigma—, así que
    contar instancias da un «165 sin ver fallar» que asusta sin informar:
    atacar la superficie 5 prueba exactamente lo mismo que atacar la 2.
    """
    n = re.sub(r"familia\[\d+\]", "familia[i]", n)
    n = re.sub(r"^(ciudad_oferta|ciudad_estudiantes|proporcion_oficial)", "<ráster>", n)
    n = re.sub(r"^(kennedy_puntos|sector_puntos)", "<puntos>", n)
    n = re.sub(r"^mapas/(ciudad_oferta|ciudad_estudiantes|proporcion_oficial)", "mapas/<ráster>", n)
    n = re.sub(r"^mapas/(kennedy_puntos|sector_puntos)", "mapas/<puntos>", n)
    n = re.sub(r"sigma=\d+", "sigma=S", n)
    n = re.sub(r"con sigma=[\d.]+ m", "con sigma=S m", n)
    n = re.sub(r"^ejercicios/e\d", "ejercicios/eN", n)
    n = re.sub(r"^kppm/\w+", "kppm/<modelo>", n)
    n = re.sub(r"en (bei/elev|bei/grad|bogotá)$", "en <covariable>", n)
    n = re.sub(r"^(está e\d)", "está eN", n)
    n = re.sub(r"ejercicios: está e\d", "ejercicios: está eN", n)
    return n


# LO QUE ESTE ARNÉS NO PUEDE ATACAR, Y NO ES UNA LAGUNA. El arnés envenena
# los JSON publicados; estas comprobaciones no los leen. Auditan la
# REIMPLEMENTACIÓN del propio auditor —la KDE recalculada, las distancias
# de geopandas, las dos dispersiones del Hawkes— contra un umbral fijo, así
# que la única forma de romperlas sería romper el auditor, que es
# precisamente lo que el arnés no debe hacer.
INATACABLES = frozenset({
    "borde: Diggle conserva el conteo a sigma=S",
    "Kennedy: las tres siguen siendo casos de frontera",
    "familia: el máximo cae al abrir el núcleo",
    "hawkes: el autoexcitado sale más agregado",
    # Compara la longitud de las dos series del MISMO CSV: el arnés
    # envenena JSON, no CSV, así que no hay por dónde tocarla.
    "hawkes: y su Poisson, los mismos",
    # Es un CANARIO: existe para que la comprobación de mojibake de al
    # lado no sea vacua, y solo puede fallar si el archivo se queda sin
    # UNA SOLA tilde. Una inyección de texto sustituye una cadena; no hay
    # forma de producir eso sin reescribir el archivo entero, que es lo
    # que un arnés no debe hacer. Se declara en vez de fingir que se
    # ataca con una sustitución inerte —que es lo que hice primero, y el
    # arnés la marcó «NO DETECTADO» con toda la razón—.
    "y hay tildes de verdad que comprobar",
})


def main() -> int:
    return arnes("prueba_auditor_cap5.py — el arnés de inyección del capítulo 5",
                 PY, AUDITOR, SALIDAS, ARCHIVOS, defectos(),
                 "genera_cap5.R y genera_soluciones.R 5",
                 agrupa=tipo, inatacables=INATACABLES)


if __name__ == "__main__":
    sys.exit(main())
