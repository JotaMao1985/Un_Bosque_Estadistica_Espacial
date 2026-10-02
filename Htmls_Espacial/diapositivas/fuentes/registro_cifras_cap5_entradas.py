"""
registro_cifras_cap5_entradas.py — el REGISTRO de `verifica_cifras_cap5.py`: cada cifra de las
presentaciones del capítulo 5, de dónde sale y cómo se comprueba.

`cargar_entradas(m, sesiones)` recibe el módulo del verificador (`m`) y registra las entradas de
las sesiones pedidas. Una cifra que aparezca en una diapositiva y no esté aquí es un ERROR.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _xj():
    t = (AQUI / "recursos" / "cap5" / "genera_figuras_s1.R").read_text(encoding="utf-8")
    return [float(x) for x in re.search(r"x_j <- c\(([^)]*)\)", t).group(1).split(",")]


def cargar_entradas(m, sesiones):
    RJ, Rr, J, J4, A, T, E, M, P, X, Spec, d, r = (m.RJ, m.Rr, m.J, m.J4, m.A, m.T, m.E, m.M, m.P, m.X, m.Spec, m.d, m.r)
    d4 = lambda ruta: m.get(m.D4, ruta)
    REG, AF, TAB = m.REG, m.AF, m.TAB

    # ------------------------------------------------------------------------------------
    # Hallazgos en el material del capítulo (se escriben en el registro; no se corrigen en silencio)
    # ------------------------------------------------------------------------------------
    m.HALLAZGOS[:] = [
        ("Los mapas ráster salen invertidos verticalmente",
         "El mapa de calor de Kennedy por σ (módulo 2), la oferta y los estudiantes (módulo 5) y P(oficial) (módulo 6) se dibujan "
         "con el sur arriba, mientras los mapas de puntos (módulos 1 y 6) van con el norte arriba. Causa: `geo_rejilla()` "
         "(`precalculo/geo.R`) guarda la fila 0 en el sur —la de `spatstat`— y `geomapaPintaRejilla()` (`plantilla-capitulo.html`) pinta "
         "la fila 0 arriba; el comentario de `geo_rejilla()` dice «de arriba a abajo, como lo espera el navegador», pero no voltea "
         "las filas. Comprobado de dos formas: con las coordenadas de las 2 107 sedes (la superficie vale más donde hay sedes solo si la "
         "fila 0 es el sur: 545 contra 457 en la oferta) y midiendo píxeles en la página servida (el punto más alto del ráster está en "
         "x = 0.46 y el del mapa de puntos en x = 0.90). El texto del módulo 5 («en el norte y en el suroccidente») es geográficamente "
         "correcto, pero el lector del capítulo ve el norte abajo. Estas diapositivas dibujan los mapas de nuevo, con el norte arriba "
         "(`recursos/cap5/genera_figuras_s1.R`). El capítulo no se modificó."),
        ("«0.0 y 24.9 sedes por km²» en la rejilla de 8 × 8",
         "El módulo 1 (y la retroalimentación de la primera pregunta de la autoevaluación) dice que los cuadrantes dan «entre 0.0 y 24.9 "
         "sedes por km²». `genera_cap5.R` calcula `conteo / (A_KEN / 64)`, o sea divide por el área media por celda de la ventana "
         "(38.51 / 64 = 0.602 km²). Pero la celda con 15 sedes es una celda interior y mide 0.895 km² (la caja entre 64): son 16.8 sedes "
         "por km² (`intensity(cuad)` da 16.757). El 24.9 no es la intensidad de ninguna celda. Además, de las 64 celdas de la rejilla, 7 "
         "caen fuera de la ventana y `quadratcount` devuelve 57. Las diapositivas solo dicen «de 0 a 15 sedes por celda»."),
        ("«Por encima de 0.965»",
         "El módulo 2 dice que las superficies de los cuatro núcleos «correlacionan por encima de 0.965 con la gaussiana». El mínimo es "
         "el del disco, 0.9647 (0.964743…), que redondea a 0.965 pero está por debajo. Las diapositivas dicen «por encima de 0.96»."),
        ("«Mayoritariamente de ese tipo»",
         "El módulo 6 dice que, donde el mapa es máximo, «los vecinos tienen que ser mayoritariamente de ese tipo». En `chorley` son el 8 % "
         "(4 de 50), y la guarda de `genera_cap5.R` compara contra la proporción global (5.6 %), no contra la mitad. Las diapositivas dicen "
         "«más que en todo el conjunto»."),
        ("La mediana no mide «en qué fracción de la ciudad son mayoría»",
         "El módulo 6 resume la mediana de la superficie P(oficial) como la respuesta a «¿en qué fracción de la ciudad son mayoría?». La "
         "mediana es el valor de la proporción en el punto típico de la ciudad (0.3086), no una fracción del área en la que las oficiales "
         "son mayoría. Las diapositivas dicen lo primero."),
        ("Los tiempos de la KDE están escritos a mano en el generador",
         "`genera_cap5.R` publica `coste_segundos = list(defecto = 0.15, sin_corregir = 0.14, diggle = 0.15)` como constantes (vienen de la "
         "medición A.21 del plan, sobre la ventana urbana a 128 × 128). Se volvieron a medir y dan lo mismo (0.146, 0.138 y 0.150 s), así que "
         "la cifra es cierta; solo que el generador no la mide. Aclaración que falta en el módulo 4: son tiempos de la ciudad, no de Kennedy "
         "(en Kennedy, a 99 × 96 celdas, son del orden de 0.01 s)."),
        ("Los valores de `bw.ppl` y `bw.CvL` son nodos de una rejilla de 16 anchos, no óptimos (módulo 3)",
         "El módulo 3 presenta `bw.ppl` y `bw.CvL` como selectores que optimizan; en realidad evalúan su criterio en `ns = 16` anchos de una "
         "rejilla geométrica y devuelven el mejor de ellos (`recomputo › selectores.ns_ppl`), y `bw.ppl` usa además `shortcut = TRUE`. Con 256 "
         "anchos, `bw.ppl` da 326 m en Kennedy y 350 m en la ciudad (no 374.9 y 235.9) y `bw.CvL`, 640 y 877 m (no 556.7 y 720.4) "
         "(`recomputo › selectores_fino`). Consecuencias: el cruce entre `bw.ppl` y `bw.diggle` que el capítulo comenta (375 contra 347 m en "
         "Kennedy, 236 contra 373 m en la ciudad) es un efecto de la rejilla, porque con rejilla fina `bw.ppl` queda por debajo de `bw.diggle` en las "
         "dos ventanas; y las razones 1.83 y 5.30, que usan esos nodos, son del orden de 2.0 y 3.6. Las diapositivas conservan las cifras del "
         "capítulo y dicen que son valores por defecto, no repiten «ni el orden se conserva» y llaman a σ = 720 m «el valor por defecto de "
         "`bw.CvL`», no «el óptimo». El capítulo no se modificó."),
        ("«El ancho mueve 13 veces lo que el núcleo» (módulo 2)",
         "La razón 66.3 / 5.1 ≈ 13 compara cuatro formas de núcleo a un solo σ (400 m) con siete σ que abarcan un factor 8, y el 5.1 % no es una "
         "constante: a otros σ el núcleo mueve el máximo más o menos. Las diapositivas dan las dos cifras por separado y no la razón."),
        ("«Si no da n, el estimador pierde o inventa sedes» (módulo 4)",
         "La integral de la intensidad es el número esperado de sedes, no el n de la muestra. Con 300 patrones al azar de 262 sedes en la ventana de "
         "Kennedy, la corrección por defecto se desvía de n en promedio +0.017 % (σ = 400 m) y +0.039 % (σ = 800 m), dentro de su error estándar "
         "(`recomputo › bordes_csr`): no es sesgada. Sin corregir se pierde un 10.3 % y un 19.6 %. El +3.19 % del patrón real (σ = 800 m) queda a "
         "más de cuatro desviaciones típicas de lo que da el azar: es del patrón, no de la corrección. Diggle conserva n por construcción. Las "
         "diapositivas dicen que la prueba mide qué conserva cada corrección, no cuál acierta."),
        ("«Las correlaciones de la versión de Python salen 0.9391, 0.8555 y 0.9155: otra discretización» (módulo 5)",
         "Con la corrección de borde por defecto de `density`, R da exactamente 0.9391, 0.8555 y 0.9155 (`recomputo › capas_defecto`); la versión de "
         "Python divide por e(u), que es la corrección por defecto. Las cifras y los mapas del capítulo usan `diggle = TRUE` (0.943, 0.862, 0.919). "
         "No es otra discretización: son dos correcciones de borde, ambas correctas. Las diapositivas lo dicen."),
        ("El máximo de `chorley` vive en la cola (módulo 6)",
         "El capítulo lee el máximo de P(laringe), 0.3389, como titular («uno de cada tres cánceres registrados es de laringe»). El píxel del "
         "máximo está a 4.6 km del punto más cercano, con σ = 1 km (el vecino 50.º, a 8.2 km): es el cociente de dos masas casi nulas. La "
         "comprobación de los 50 vecinos (4 casos de 50) detecta un mapa invertido, pero no valida el máximo. Las diapositivas no lo leen como "
         "riesgo y la figura usa la escala fija de 0 a 1."),
        ("La corrección de borde «se cancela» en el cociente (módulo 6)",
         "Solo con la corrección por defecto, donde el mismo e(u) divide numerador y denominador; con `diggle = TRUE` cada sede se divide por su "
         "propio e(x_i) y no se cancela. Las diapositivas lo dicen así."),
        ("Los tiempos «555 veces» y «1.07» (módulo 4)",
         "El cociente 122.655 / 0.221 = 555 es una medición de tiempo y depende de la máquina y del momento (al volver a medir salen cientos de "
         "veces, no exactamente 555), y el 1.07 sale de dos cifras redondeadas a centésimas (0.15 / 0.14). Las diapositivas dicen «cientos de "
         "veces» y «del mismo orden»."),
        ("Kennedy no está contenida en la ventana urbana (módulo 1)",
         "3 de las 262 sedes de Kennedy y el 9.8 % de su área caen fuera del perímetro urbano (`recomputo › kennedy`): son capas con ventanas "
         "distintas, de modo que «Kennedy dentro de la ciudad» es aproximado. Va en las notas."),
        ("El Quiz 2 cubre los módulos 1 a 4 (módulo 13)",
         "El módulo 13 dice que las preguntas de este capítulo en el Quiz 2 son de los módulos 1 a 4. Las notas de la primera versión de las "
         "diapositivas decían que el módulo 5 entraba «en lo que toca a la resolución de la rejilla» y que las ocho preguntas del módulo 12 "
         "eran para hacerlas antes del Quiz 2 (cuatro de ellas son de la sesión 2). Corregido en las notas."),
    ]

    if 1 in sesiones:
        S1 = ("Portada",)

        # ---- portada y arranque ----
        REG("90", P("duración de la clase pedida por el docente (90 min), decisión D1; no es un dato del capítulo"), en=("Portada", "De contar a suavizar"))
        REG("29.5", RJ("m2.familia.max_km2[0]", "anchos.picos_km2[0]"))
        REG("3.5.1", J("meta.paquetes.spatstat"))

        # ---- módulo 1 ----
        REG("5.69", [Rr("urbana.lambda_km2"), T("5.6932")])
        REG("12.25", T("versión 12.25", corpus="fuentes"))
        REG("2209", Rr("urbana.n_capa"))
        REG("2107", RJ("m5.capas.oferta.n", "urbana.n_urbana"))
        REG("9377", T("EPSG:9377"))
        REG("370.09", Rr("urbana.area_km2"))
        REG("262", RJ("m1.ventana.n", "kennedy.n"))
        REG("38.51", RJ("m1.ventana.area_km2", "kennedy.area_km2"))
        REG("6.80", RJ("m1.ventana.lambda_km2", "kennedy.lambda_km2"))
        REG("261", RJ("m1.frontera.n_atributo", "kennedy.n_atributo"))
        REG("7.5", RJ("m1.ventana.caja_x_km", "kennedy.caja_x_km"))
        REG("7.7", RJ("m1.ventana.caja_y_km", "kennedy.caja_y_km"))
        REG("87", J("m1.frontera.dist_max_m"))
        REG("8x8", [P("rejilla de 8 × 8 del capítulo", "m1.cuadrantes.nx"), Rr("cuadrantes.nx")])
        REG("15", [RJ("m1.cuadrantes.conteo_max", "cuadrantes.conteo_max"), Rr("cuadrantes.rango_desplazados[0]")])
        REG("21", Rr("cuadrantes.rango_desplazados[1]"))
        REG("16", Rr("cuadrantes.desplazamientos"), cx=r"16 posiciones|16 desplazamientos")
        REG("64", RJ("m1.cuadrantes.n_celdas", "cuadrantes.celdas_rejilla"), cx=r"celdas de la rejilla")
        REG("7", A(lambda: r("cuadrantes.celdas_rejilla") - r("cuadrantes.celdas_con_ventana"), "64 celdas de la rejilla − 57 con ventana"))
        REG("10", [P("distancia ilustrativa del texto del capítulo («aunque esté a diez metros»)"), T("a diez metros")], cx=r"a 10 m")
        REG(["1.2", "1.9", "2.3", "6.5", "7.9", "8.4"],
            Spec("param", "posiciones inventadas de la ilustración (`x_j` en `genera_figuras_s1.R`)", [("genera_figuras_s1.R › x_j", _xj)]))

        # ---- módulo 2 ----
        REG("400", [RJ("m2.sigma_m", "nucleos.sigma_m"), J("m4.sigmas_m")])
        REG("233", RJ("m2.familia.sigmas_m[0]", "anchos.sigmas_m[0]"))
        REG("660", RJ("m2.familia.sigmas_m[3]", "anchos.sigmas_m[3]"))
        REG("1867", RJ("m2.familia.sigmas_m[6]", "anchos.sigmas_m[6]"))
        REG(["10", "50"], P("órdenes de magnitud que se le piden al grupo antes de revelar; no son datos"), cx=r"¿10 %\?|¿50 %\?")
        REG("18.45", RJ("m2.nucleos.max_km2.gaussian", "nucleos.max_km2.gaussian"))
        REG("17.51", RJ("m2.nucleos.max_km2.epanechnikov", "nucleos.max_km2.epanechnikov"))
        REG("17.69", RJ("m2.nucleos.max_km2.quartic", "nucleos.max_km2.quartic"))
        REG("17.88", RJ("m2.nucleos.max_km2.disc", "nucleos.max_km2.disc"))
        REG("18.4483", RJ("m2.nucleos.max_km2.gaussian", "nucleos.max_km2.gaussian"))
        REG("17.5145", RJ("m2.nucleos.max_km2.epanechnikov", "nucleos.max_km2.epanechnikov"))
        REG("17.6900", RJ("m2.nucleos.max_km2.quartic", "nucleos.max_km2.quartic"))
        REG("17.8808", RJ("m2.nucleos.max_km2.disc", "nucleos.max_km2.disc"))
        REG("0.9911", RJ("m2.nucleos.cor_con_gaussiano.epanechnikov", "nucleos.cor_gauss.epanechnikov"))
        REG("0.9958", RJ("m2.nucleos.cor_con_gaussiano.quartic", "nucleos.cor_gauss.quartic"))
        REG("0.9647", RJ("m2.nucleos.cor_con_gaussiano.disc", "nucleos.cor_gauss.disc"))
        REG(["5.1", "5.0616"], RJ("m2.nucleos.max_dif_pct", "nucleos.dif_pct"))
        REG("0.96", A(lambda: 0.96 if min(r("nucleos.cor_gauss.epanechnikov"), r("nucleos.cor_gauss.quartic"), r("nucleos.cor_gauss.disc")) > 0.96 else -1,
                      "la menor de las tres correlaciones (0.9647) supera 0.96"))
        REG("0.965", T("por encima de 0.965"))
        REG("9.9", RJ("m2.familia.max_km2[6]", "anchos.picos_km2[6]"))
        REG("21.6", RJ("m2.familia.max_km2[1]", "anchos.picos_km2[1]"))
        REG("16.8", RJ("m2.familia.max_km2[2]", "anchos.picos_km2[2]"))
        REG("13.8", RJ("m2.familia.max_km2[3]", "anchos.picos_km2[3]"))
        REG("11.9", RJ("m2.familia.max_km2[4]", "anchos.picos_km2[4]"))
        REG("10.9", RJ("m2.familia.max_km2[5]", "anchos.picos_km2[5]"))
        REG("96x99", Spec("param", "rejilla de la familia de σ (nx × ny)", [("datos › m2.familia.nx × ny", lambda: f"{d('m2.familia.nx')}x{d('m2.familia.ny')}")]))
        REG("29.507", RJ("m2.familia.max_km2[0]", "anchos.picos_km2[0]"))
        REG("9.946", RJ("m2.familia.max_km2[6]", "anchos.picos_km2[6]"))
        REG(["66.3", "66.291"], RJ("m2.familia.caida_pct", "anchos.caida_pct"))
        REG("66.4", Rr("anchos.caida_con_redondeo_1dec"))
        REG("13", Rr("anchos.veces_el_nucleo"), cx=r"13 veces")
        REG("78", RJ("m2.familia.celda_m", "anchos.celda_x_m"))

        # ---- módulo 3 ----
        REG("347.1", RJ("m3.kennedy.sigmas_m.diggle", "selectores.kennedy.sigmas_m.diggle"))
        REG("374.9", RJ("m3.kennedy.sigmas_m.ppl", "selectores.kennedy.sigmas_m.ppl"))
        REG("556.7", RJ("m3.kennedy.sigmas_m.CvL", "selectores.kennedy.sigmas_m.CvL"))
        REG("633.6", RJ("m3.kennedy.sigmas_m.scott", "selectores.kennedy.sigmas_m.scott"))
        REG("373.2", RJ("m3.urbana.sigmas_m.diggle", "selectores.ciudad.sigmas_m.diggle"))
        REG("235.9", RJ("m3.urbana.sigmas_m.ppl", "selectores.ciudad.sigmas_m.ppl"))
        REG("720.4", RJ("m3.urbana.sigmas_m.CvL", "selectores.ciudad.sigmas_m.CvL"))
        REG("1251.3", RJ("m3.urbana.sigmas_m.scott", "selectores.ciudad.sigmas_m.scott"))
        REG("1.83", RJ("m3.kennedy.razon", "selectores.kennedy.razon"), cx=r"Kennedy")
        REG("5.30", RJ("m3.urbana.razon", "selectores.ciudad.razon"), cx=r"ciudad|Ciudad|selectores se abren")
        REG("634", RJ("m3.kennedy.sigmas_m.scott", "selectores.kennedy.sigmas_m.scott"))
        REG("580", RJ("m3.kennedy.scott_y_m", "selectores.kennedy.scott_y_m"))
        REG("1251", RJ("m3.urbana.sigmas_m.scott", "selectores.ciudad.sigmas_m.scott"))
        REG("2197", RJ("m3.urbana.scott_y_m", "selectores.ciudad.scott_y_m"))
        REG("375", RJ("m3.kennedy.sigmas_m.ppl", "selectores.kennedy.sigmas_m.ppl"))
        REG("347", RJ("m3.kennedy.sigmas_m.diggle", "selectores.kennedy.sigmas_m.diggle"))
        REG("236", RJ("m3.urbana.sigmas_m.ppl", "selectores.ciudad.sigmas_m.ppl"))
        REG("373", RJ("m3.urbana.sigmas_m.diggle", "selectores.ciudad.sigmas_m.diggle"))
        REG("550", RJ("m5.rejilla.sigma_minimo_dibujable_m", "capas.sigma_minimo_m"))
        REG("65", [Rr("japanesepines.n"), E("japanesepines.ayuda", "65 tree sapling")])
        REG("5.7", E("japanesepines.ayuda", "5.7 x 5.7 metre square"))
        REG("1961", E("japanesepines.ayuda", "Numata (1961)"))
        REG("0.7071", RJ("m3.topes[0].sigma", "japanesepines.bw_ppl"))
        REG("20", T("con el tope subido a 20"))

        # ---- módulo 4 ----
        REG("555", J4("m10.coste.veces_isotropica_sobre_traslacion"))
        REG(["200", "800"], J("m4.sigmas_m"))
        REG("255.08", RJ("m4.tabla[0].masa_sin_corregir", "bordes.200.masa_sin"))
        REG("-2.64", RJ("m4.tabla[0].fuga_sin_corregir_pct", "bordes.200.pct_sin"))
        REG("263.30", RJ("m4.tabla[0].masa_defecto", "bordes.200.masa_defecto"))
        REG("0.50", RJ("m4.tabla[0].exceso_defecto_pct", "bordes.200.pct_defecto"))
        REG("262.00", [RJ("m4.tabla[0].masa_diggle", "bordes.200.masa_diggle"), RJ("m4.tabla[2].masa_diggle", "bordes.800.masa_diggle")], cx=r"[Dd]iggle|\\| 2[0-9][0-9]\\.")
        REG("0.0000", [RJ("m4.tabla[0].error_diggle_pct", "bordes.200.pct_diggle"), RJ("m4.tabla[2].error_diggle_pct", "bordes.800.pct_diggle")])
        REG("245.86", RJ("m4.tabla[1].masa_sin_corregir", "bordes.400.masa_sin"))
        REG("-6.16", RJ("m4.tabla[1].fuga_sin_corregir_pct", "bordes.400.pct_sin"))
        REG("265.80", RJ("m4.tabla[1].masa_defecto", "bordes.400.masa_defecto"))
        REG("1.45", RJ("m4.tabla[1].exceso_defecto_pct", "bordes.400.pct_defecto"))
        REG("224.41", RJ("m4.tabla[2].masa_sin_corregir", "bordes.800.masa_sin"))
        REG("-14.35", RJ("m4.tabla[2].fuga_sin_corregir_pct", "bordes.800.pct_sin"))
        REG(["270.36", "270.3619"], RJ("m4.tabla[2].masa_defecto", "bordes.800.masa_defecto"), cx=r"por defecto")
        REG("3.19", RJ("m4.tabla[2].exceso_defecto_pct", "bordes.800.pct_defecto"))
        REG("17.54", RJ("m4.horquilla_pct", "bordes.horquilla_pp_800"))
        REG("12.66", RJ("m4.tabla[2].max_km2_defecto", "bordes.800.max_defecto"))
        REG("11.54", RJ("m4.tabla[2].max_km2_sin_corregir", "bordes.800.max_sin"))
        REG("3", A(lambda: 3 if r("diggle_identidad.error_pct_diggle") < 3 and r("diggle_identidad.error_pct_defecto") < 3 else -1,
                   "el error de ambas fórmulas contra spatstat (2.87 % y 2.54 %) es menor que 3 %"), cx=r"menos de 3 %")
        REG("88", Rr("diggle_identidad.cruce_pct"))
        REG("99x96", Spec("param", "rejilla de `density(..., dimyx = c(99, 96))` (ny × nx)", [("datos › m2.familia.ny × nx", lambda: f"{d('m2.familia.ny')}x{d('m2.familia.nx')}")]))
        REG("262.0000", RJ("m4.tabla[2].masa_diggle", "bordes.800.masa_diggle"))
        REG("224.4065", RJ("m4.tabla[2].masa_sin_corregir", "bordes.800.masa_sin"))
        REG("128x128", P("rejilla de 128 × 128 celdas sobre la ventana urbana", "meta.rejilla.nx_ciudad"))
        REG("0.221", J4("m10.correcciones[2].segundos"))
        REG("122.655", J4("m10.correcciones[3].segundos"))
        REG("0.14", J("m4.coste_segundos.sin_corregir"))
        REG("0.15", [J("m4.coste_segundos.defecto"), J("m4.coste_segundos.diggle")])
        REG("1.07", A(lambda: d("m4.coste_segundos.defecto") / d("m4.coste_segundos.sin_corregir"), "0.15 / 0.14"))
        REG("0.146", M("tiempos.ciudad_128.defecto", 0.02))
        REG("0.138", M("tiempos.ciudad_128.sin_corregir", 0.02))
        REG("0.150", M("tiempos.ciudad_128.diggle", 0.02))

        # ---- módulo 5 ----
        REG("20224", T("periodo 20224", corpus="fuentes"))
        REG("11", P("grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11"), cx=r"grado 11|Saber 11")
        REG("720", RJ("m5.sigma_m", "capas.sigma_m"))
        REG("14.54", RJ("m5.capas.oferta.max_km2", "capas.max_oferta"))
        REG("1062", RJ("m5.capas.grado_11.n", "capas.n_grado11"))
        REG("50.4", RJ("m5.capas.grado_11.pct_de_las_sedes", "capas.pct_grado11"))
        REG("9.54", RJ("m5.capas.grado_11.max_km2", "capas.max_grado11"))
        REG("145362", RJ("m5.capas.estudiantes.total", "capas.evaluados"))
        REG("1578.81", RJ("m5.capas.estudiantes.max_km2", "capas.max_estudiantes"))
        REG("0.943", RJ("m5.cor_oferta_grado11", "capas.cor_of_11"))
        REG("0.862", RJ("m5.cor_oferta_estudiantes", "capas.cor_of_es"))
        REG("0.919", RJ("m5.cor_grado11_estudiantes", "capas.cor_11_es"))
        REG(["0.9391", "0.8555", "0.9155"], T("0.9391, 0.8555, 0.9155"))
        REG("128x218", Spec("param", "rejilla de la ciudad (nx × ny)", [("datos › m5.rejilla.nx × ny", lambda: f"{d('m5.rejilla.nx')}x{d('m5.rejilla.ny')}")]))
        REG("183", RJ("m5.rejilla.celda_m", "capas.celda_x_m"))
        REG("183.4", RJ("m5.rejilla.celda_m", "capas.celda_x_m"))
        REG("14.5", RJ("m5.capas.oferta.max_km2", "capas.max_oferta"))
        REG("1579", RJ("m5.capas.estudiantes.max_km2", "capas.max_estudiantes"))
        REG("3", J("meta.rejilla.celdas_por_sigma"), cx=r"3 celdas|3 × 183|σ/3|regla de 3")

        # ---- módulo 6 ----
        REG("58", RJ("m6.chorley.casos", "chorley.n_laringe"), cx=r"casos|laringe|58 /")
        REG("978", RJ("m6.chorley.controles", "chorley.n_pulmon"), cx=r"pulmón|controles")
        REG("1036", Rr("chorley.n"))
        REG("315.16", Rr("chorley.area_km2"))
        REG(["1974", "1983"], E("chorley.ayuda", "between 1974 and 1983"))
        REG("1990", E("chorley.ayuda", "Diggle (1990)"))
        REG("0.0560", RJ("m6.chorley.prop_global", "chorley.global"))
        REG("0.0482", RJ("m6.chorley.p_mediana", "chorley.mediana"))
        REG("0.3389", RJ("m6.chorley.p_max", "chorley.maximo"))
        REG("6", Rr("chorley.maximo_sobre_global"))
        REG("4", Rr("chorley.vecinos_casos"), cx=r"4 de (los |sus )?50")
        REG("50", Rr("chorley.vecinos_k"), cx=r"vecinos|de 50")
        REG("0.6914", Rr("oficial.mediana_sin_fijar_niveles"))
        REG("0.3086", RJ("m6.bogota.p_mediana", "oficial.mediana"))
        REG("8", [A(lambda: 100 * d("m6.chorley.orientacion_verificada"), "100 × orientación del máximo de chorley"), A(lambda: 100 * r("chorley.vecinos_prop"), "100 × vecinos casos / 50")])
        REG("5.6", A(lambda: 100 * d("m6.chorley.prop_global"), "100 × proporción global de chorley"))
        REG("64", [A(lambda: 100 * d("m6.bogota.orientacion_verificada"), "100 × orientación del máximo de Bogotá"), A(lambda: 100 * r("oficial.vecinos_prop"), "100 × vecinos oficiales / 50")], cx=r"64 %")
        REG("32", Rr("oficial.vecinos_oficiales"))
        REG("33.65", A(lambda: 100 * d("m6.bogota.prop_global"), "100 × proporción global de oficiales"))
        REG("0.9518", Rr("chorley.mediana_sin_fijar_niveles"))
        REG("709", RJ("m6.bogota.oficiales", "oficial.n_oficiales"), cx=r"709\*{0,2} oficiales|709 / 2")
        REG("1398", RJ("m6.bogota.privadas", "oficial.n_privadas"), cx=r"1.?398\*{0,2} privadas")
        REG("0.3365", RJ("m6.bogota.prop_global", "oficial.global"), cx=r"puntos|709 / 2")
        REG("0.028", [A(lambda: abs(d("m6.bogota.brecha_mediana_menos_global")), "|mediana − global| en el JSON"), Rr("oficial.brecha")])

        # ---- cierre ----
        REG("0.5", T("sigma = 0.5, 1 y 2"), cx=r"σ = 0\.5|sigma = 0\.5")

        # ---- revisión del 1 oct 2026 (revisión pedagógica y auditoría de cifras independientes) ----
        Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
        REG(["13", "11", "14", "10", "4"], P("minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo"),
            en=("De contar a suavizar", "Núcleo y ancho de banda", "Selectores de ancho de banda", "Corrección de borde en la KDE",
                "La KDE como mapa de calor", "Intensidad relativa", "Cierre y práctica"),
            cx=r"min|este módulo|núcleo y ancho|selectores|corrección de borde|mapa de calor|intensidad relativa|cierre y práctica")
        REG("3", Rr("kennedy.sedes_fuera_de_la_urbana"), cx=r"3 de sus 262")
        REG("9.8", Rr("kennedy.area_fuera_de_la_urbana_pct"))
        REG(["30", "60", "5", "10"], P("opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos"),
            cx=r"en torno al 30|mueve el máximo un (60|5) %|ancho, un (5|60) %|pasa del 10 %")
        REG("1.67", A(lambda: max(r("selectores.kennedy.scott_y_m"), r("selectores.kennedy.sigmas_m.CvL")) / r("selectores.kennedy.sigmas_m.diggle"),
                      "cociente máximo / mínimo de los selectores de Kennedy con el ancho del eje y de `bw.scott`"))
        REG("9.31", A(lambda: r("selectores.ciudad.scott_y_m") / r("selectores.ciudad.sigmas_m.ppl"),
                      "cociente máximo / mínimo de los selectores de la ciudad con el ancho del eje y de `bw.scott`"))
        REG("256", Rr("selectores_fino.ns"))
        REG("326", Rr("selectores_fino.kennedy.ppl"))
        REG("350", Rr("selectores_fino.ciudad.ppl"))
        REG("640", Rr("selectores_fino.kennedy.CvL"))
        REG("877", Rr("selectores_fino.ciudad.CvL"))
        REG("16", Rr("selectores.ns_ppl"), cx=r"16 anchos")
        REG("69", A(lambda: 100 * Phi(0.5), "100 × Φ(0.5): la fracción del núcleo de una sede a 0.5 σ del borde que queda dentro de la ventana"))
        REG("0.69", A(lambda: Phi(0.5), "Φ(0.5)"))
        REG("31", A(lambda: 100 * (1 - Phi(0.5)), "100 × (1 − Φ(0.5)): lo que se sale"))
        REG("0.5", P("distancia de la sede al borde, en unidades de σ, en la ilustración en una dimensión"), cx=r"0\.5 σ|normal en 0\.5")
        REG("0.5", P("umbral de mayoría de P(oficial): más de la mitad"), cx=r"> 0\.5")
        REG("270.4", RJ("m4.tabla[2].masa_defecto", "bordes.800.masa_defecto"))
        REG("224.4", RJ("m4.tabla[2].masa_sin_corregir", "bordes.800.masa_sin"))
        REG("262.0", RJ("m4.tabla[2].masa_diggle", "bordes.800.masa_diggle"))
        REG("0.155", M("tiempos.ciudad_128.defecto", 0.02))
        REG("0.147", M("tiempos.ciudad_128.sin_corregir", 0.02))
        REG("0.161", M("tiempos.ciudad_128.diggle", 0.02))
        REG("9.5", RJ("m5.capas.grado_11.max_km2", "capas.max_grado11"))
        REG("17.5", Rr("oficial.area_mayoria_oficial_pct"))
        REG("4.6", Rr("chorley.max_dist_punto_mas_cercano_km"), cx=r"4\.6 km")
        REG("300", Rr("bordes_csr.patrones"), cx=r"300 patrones")
        REG("0.04", Rr("bordes_csr.media_pct.defecto_800"))
        REG("-19.6", Rr("bordes_csr.media_pct.sin_800"))

        # ---- afirmaciones que no son una cifra ----
        AF(1, "El máximo de la oferta cae en Suba y el de estudiantes, en Bosa", lambda: r("capas_maximos.localidad_max_oferta") == "Suba" and r("capas_maximos.localidad_max_estudiantes") == "Bosa")
        AF(1, "`bw.ppl(japanesepines)` devuelve exactamente la mitad del diámetro de la ventana (el tope de su intervalo)", lambda: abs(r("japanesepines.bw_ppl") - r("japanesepines.tope_intervalo")) < 1e-9)
        AF(1, "R avisa de que el criterio se maximizó en el extremo derecho del intervalo", lambda: any("right-hand end of interval" in a for a in (r("japanesepines.aviso") if isinstance(r("japanesepines.aviso"), list) else [r("japanesepines.aviso")])))
        AF(1, "Con el intervalo ampliado a 2, `bw.ppl` devuelve 2 (otra pared) y el criterio sigue subiendo", lambda: r("japanesepines.optimo_con_srange_2") == 2 and all(b > a for a, b in zip(r("japanesepines.criterio_cv")[4:], r("japanesepines.criterio_cv")[5:])))
        AF(1, "Con los valores por defecto, `bw.ppl` queda por encima de `bw.diggle` en Kennedy y por debajo en la ciudad (el cruce que comenta el capítulo)", lambda: r("selectores.kennedy.sigmas_m.ppl") > r("selectores.kennedy.sigmas_m.diggle") and r("selectores.ciudad.sigmas_m.ppl") < r("selectores.ciudad.sigmas_m.diggle"))
        AF(1, "Con 256 anchos, `bw.ppl` queda por debajo de `bw.diggle` en las dos ventanas: el cruce es un efecto de la rejilla de 16 anchos", lambda: r("selectores_fino.kennedy.ppl") < r("selectores.kennedy.sigmas_m.diggle") and r("selectores_fino.ciudad.ppl") < r("selectores.ciudad.sigmas_m.diggle"))
        AF(1, "`bw.ppl` y `bw.CvL` evalúan su criterio en 16 anchos (`ns = 16`) y `bw.ppl` usa `shortcut = TRUE`", lambda: r("selectores.ns_ppl") == 16 and r("selectores.ns_cvl") == 16 and r("selectores.shortcut_ppl") is True)
        AF(1, "El abanico de los selectores se abre más en la ciudad que en Kennedy, también con 256 anchos", lambda: r("selectores.ciudad.razon") > r("selectores.kennedy.razon") and max(r("selectores.ciudad.sigmas_m.scott"), r("selectores_fino.ciudad.CvL")) / min(r("selectores.ciudad.sigmas_m.diggle"), r("selectores_fino.ciudad.ppl")) > max(r("selectores.kennedy.sigmas_m.scott"), r("selectores_fino.kennedy.CvL")) / min(r("selectores.kennedy.sigmas_m.diggle"), r("selectores_fino.kennedy.ppl")))
        AF(1, "Sobre 300 patrones al azar de 262 sedes, la corrección por defecto conserva n en promedio (desviación media menor que 0.1 % en valor absoluto) y sin corregir se pierde más del 10 %", lambda: abs(r("bordes_csr.media_pct.defecto_400")) < 0.1 and abs(r("bordes_csr.media_pct.defecto_800")) < 0.1 and r("bordes_csr.media_pct.sin_400") < -10 and r("bordes_csr.media_pct.sin_800") < -10)
        AF(1, "El +3.19 % de la corrección por defecto en Kennedy (σ = 800 m) queda a más de 3 desviaciones típicas de lo que da el azar", lambda: (r("bordes.800.pct_defecto") - r("bordes_csr.media_pct.defecto_800")) / r("bordes_csr.sd_pct.defecto_800") > 3)
        AF(1, "Las correlaciones de la versión de Python (0.9391, 0.8555, 0.9155) son las de la corrección de borde por defecto", lambda: all(abs(r(f"capas_defecto.{k}") - v) < 5e-5 for k, v in (("cor_of_11", 0.9391), ("cor_of_es", 0.8555), ("cor_11_es", 0.9155))))
        AF(1, "El píxel del máximo de P(laringe) queda a más de 3 km del punto más cercano (con σ = 1 km): es la cola", lambda: r("chorley.max_dist_punto_mas_cercano_km") > 3)
        AF(1, "Las oficiales son mayoría (P > 0.5) en menos de una quinta parte del área", lambda: r("oficial.area_mayoria_oficial_pct") < 20)
        AF(1, "Kennedy no está contenida en la ventana urbana: parte de sus sedes y de su área caen fuera del perímetro", lambda: r("kennedy.sedes_fuera_de_la_urbana") > 0 and r("kennedy.area_fuera_de_la_urbana_pct") > 0)
        AF(1, "Sobre la ciudad, `bw.diggle` y `bw.ppl` quedan por debajo de 3 celdas (550 m) y `bw.CvL` y `bw.scott`, por encima", lambda: max(r("selectores.ciudad.sigmas_m.diggle"), r("selectores.ciudad.sigmas_m.ppl")) < r("capas.sigma_minimo_m") <= min(r("selectores.ciudad.sigmas_m.CvL"), r("selectores.ciudad.sigmas_m.scott")))
        AF(1, "`bw.CvL` es el más estrecho de los dos selectores que la rejilla de la ciudad puede dibujar", lambda: r("selectores.ciudad.sigmas_m.CvL") < r("selectores.ciudad.sigmas_m.scott"))
        AF(1, "Sin corregir, la masa queda por debajo de n y la fuga crece con σ; por defecto, queda por encima y el exceso crece con σ; con diggle es n", lambda: all(r(f"bordes.{s}.masa_sin") < 262 < r(f"bordes.{s}.masa_defecto") and abs(r(f"bordes.{s}.masa_diggle") - 262) < 1e-9 for s in ("200", "400", "800")) and r("bordes.200.pct_sin") > r("bordes.400.pct_sin") > r("bordes.800.pct_sin") and r("bordes.200.pct_defecto") < r("bordes.400.pct_defecto") < r("bordes.800.pct_defecto"))
        AF(1, "El pico baja al no corregir (σ = 800 m)", lambda: r("bordes.800.max_sin") < r("bordes.800.max_defecto"))
        AF(1, "Los tres tiempos de la KDE sobre la ciudad son del mismo orden (cociente máximo / mínimo menor que 1.3)", lambda: max(r("tiempos.ciudad_128").get(k, 0) for k in ("defecto", "sin_corregir", "diggle")) / min(r("tiempos.ciudad_128")[k] for k in ("defecto", "sin_corregir", "diggle")) < 1.3)
        AF(1, "La fórmula de Diggle a mano coincide con spatstat (menos de 3 %) y la del defecto, usada en su lugar, no (más de 50 %)", lambda: r("diggle_identidad.error_pct_diggle") < 3 and r("diggle_identidad.cruce_pct") > 50)
        AF(1, "La caja que enmarca a Kennedy no es la ventana: su área (7.5 × 7.7 km) es mayor que la de la ventana", lambda: r("kennedy.caja_x_km") * r("kennedy.caja_y_km") > r("kennedy.area_km2") * 1.2)
        AF(1, "Sin fijar el orden de niveles, el mapa de chorley es P(pulmón) y el de Bogotá, P(privado): la mediana es el complemento", lambda: abs(r("chorley.mediana_sin_fijar_niveles") - (1 - r("chorley.mediana"))) < 5e-4 and abs(r("oficial.mediana_sin_fijar_niveles") - r("oficial.complemento_de_la_mediana")) < 5e-4)
        AF(1, "En el máximo de P(laringe) los casos pesan más que en el conjunto, sin ser mayoría (8 % contra 5.6 %)", lambda: r("chorley.vecinos_prop") > r("chorley.global") and r("chorley.vecinos_prop") < 0.5)
        AF(1, "En el máximo de P(oficial) las oficiales pesan más que en el conjunto (64 % contra 33.65 %)", lambda: r("oficial.vecinos_prop") > r("oficial.global"))
        AF(1, "La mediana de la superficie P(oficial) queda por debajo de la proporción de los puntos", lambda: r("oficial.mediana") < r("oficial.global"))
        AF(1, "Las tres correlaciones de las capas son menores que 1 y la menor es la de oferta con estudiantes", lambda: max(r("capas.cor_of_11"), r("capas.cor_of_es"), r("capas.cor_11_es")) < 1 and r("capas.cor_of_es") == min(r("capas.cor_of_11"), r("capas.cor_of_es"), r("capas.cor_11_es")))
        AF(1, "La integral de la KDE ponderada por evaluados da el total de evaluados", lambda: abs(r("capas.integral_estudiantes") - r("capas.evaluados")) < 1)

        # ---- «al subir σ, los picos bajan y los valles se llenan» (lámina 8, la ilustración; notas de la 9, la animación) ----
        # No es «baja el mapa entero»: baja donde estaba alto y sube donde estaba bajo. Lo que dice cada frase, medido en R con los
        # mismos datos (`recomputa_cap5_picos_valles.R` lee los puntos y los σ de `genera_figuras_s1.R` y del motor).
        NUC4 = ("gaussian", "epanechnikov", "quartic", "disc")
        AF(1, "Ilustración de la lámina 8 (seis puntos, núcleo gaussiano, σ de 0.35 a 1.2): el máximo de la suma baja, en el valle entre los dos grupos sube, y el 10 % más alto baja y la mitad más baja sube",
           lambda: r("picos_valles.juguete.max_ancho") < r("picos_valles.juguete.max_estrecho") and r("picos_valles.juguete.valle_ancho") > r("picos_valles.juguete.valle_estrecho")
           and r("picos_valles.juguete.alta_baja") > 0.99 and r("picos_valles.juguete.baja_sube") > 0.99)
        AF(1, "Animación del módulo 1 (19 puntos, σ de 0.5 a 2.2, sin corregir el borde), con los cuatro núcleos: del σ más estrecho al más ancho el 10 % más alto de la superficie baja y la mitad más baja sube",
           lambda: all(r(f"picos_valles.conteo.por_nucleo.{k}.alta_baja") > 0.99 and r(f"picos_valles.conteo.por_nucleo.{k}.baja_sube") > 0.99 for k in NUC4))
        AF(1, "Animación del módulo 1: con el gaussiano, el epanechnikov y el cuártico el máximo no sube en ningún paso del deslizador de σ; con el disco sube en algunos",
           lambda: all(r(f"picos_valles.conteo.por_nucleo.{k}.pasos_sube") == 0 for k in NUC4[:3]) and r("picos_valles.conteo.por_nucleo.disc.pasos_sube") >= 1)
        AF(1, "Con el disco, el máximo sube justo en los pasos en que el mejor círculo alcanza un punto más (el conteo máximo de puntos dentro del círculo aumenta)",
           lambda: bool(r("picos_valles.conteo.por_nucleo.disc.salto_con_mas_puntos")))

        # ---- tablas: cada celda numérica en su casilla ----
        nk = lambda k: (lambda: r(f"nucleos.max_km2.{k}"))
        ck = lambda k: (lambda: r(f"nucleos.cor_gauss.{k}"))
        TAB(1, "Cambiar el núcleo mueve el máximo", [
            [None, [nk("gaussian")], None],
            [None, [nk("epanechnikov")], [ck("epanechnikov")]],
            [None, [nk("quartic")], [ck("quartic")]],
            [None, [nk("disc")], [ck("disc")]]])
        sk = lambda v_: (lambda: r(f"selectores.kennedy.sigmas_m.{v_}"))
        sc = lambda v_: (lambda: r(f"selectores.ciudad.sigmas_m.{v_}"))
        TAB(1, "Cada selector le pregunta", [
            [None, None, [sk("diggle")], [sc("diggle")]],
            [None, None, [sk("ppl")], [sc("ppl")]],
            [None, None, [sk("CvL")], [sc("CvL")]],
            [None, None, [sk("scott")], [sc("scott")]]])
        b3 = lambda s_, k: (lambda: r(f"bordes.{s_}.{k}"))
        TAB(1, "Medido sobre Kennedy", [
            [[200], [b3("200", "masa_sin"), b3("200", "pct_sin")], [b3("200", "masa_defecto"), b3("200", "pct_defecto")], [b3("200", "masa_diggle"), b3("200", "pct_diggle")]],
            [[400], [b3("400", "masa_sin"), b3("400", "pct_sin")], [b3("400", "masa_defecto"), b3("400", "pct_defecto")], [b3("400", "masa_diggle"), b3("400", "pct_diggle")]],
            [[800], [b3("800", "masa_sin"), b3("800", "pct_sin")], [b3("800", "masa_defecto"), b3("800", "pct_defecto")], [b3("800", "masa_diggle"), b3("800", "pct_diggle")]]])
        TAB(1, "Con celdas de 183 m", [
            [None, [sc("diggle")], None], [None, [sc("ppl")], None], [None, [sc("CvL")], None], [None, [sc("scott")], None]])

    # ====================================================================================
    # SESIÓN 2 · módulos 7 a 11 y el proyecto integrador
    # ====================================================================================
    if 2 in sesiones:
        def LJ(rutas_json, rutas_rec, desc=""):
            """JSON del capítulo Y recómputo: la cifra puede ser cualquiera de varios valores (todos bajo la misma etiqueta)."""
            return Spec("rj", desc, [("datos › " + ", ".join(rutas_json), lambda: [d(x) for x in rutas_json]),
                                     ("recomputo › " + ", ".join(rutas_rec), lambda: [r(x) for x in rutas_rec])])

        def RA(ruta_json, fn, desc):
            """JSON del capítulo Y una cuenta sobre el recómputo en R."""
            return Spec("rj", desc, [("datos › " + ruta_json, lambda: d(ruta_json)), (desc, fn)])

        MODELOS = ("Thomas", "MatClust", "LGCP")
        DIVISORES = ("De estimar a modelar", "Covariables", "El Poisson inhomogéneo", "Ajustar con ppm", "Diagnóstico del ajuste",
                     "Conglomerado y autoexcitación", "El proyecto integrador y la práctica")
        RHO = "`rhohat` es aleatorio"

        m.HALLAZGOS.extend([
            (2, "La ayuda de `bei` habla de 3605 árboles; el conjunto trae 3 604",
             "La ficha de ayuda de `bei` (spatstat.data) dice «the locations of 3605 trees», pero `npoints(bei)` es 3604 "
             "(`recomputo › m7.bei.n`), que es la cifra del capítulo. Las diapositivas usan 3 604 y lo advierten en las notas."),
            (2, "«entre 21.12 y 21.14» (módulo 7)",
             "El comentario del bloque de `rhohat` dice que la razón de la elevación «se mueve entre 21.12 y 21.14» sin tocar el dato. "
             "Con 20 semillas distintas (`recomputo › m7_semillas`) va de 21.10 a 21.15 (y con las semillas 2001 a 2020, de 21.0996 a "
             "21.1592, según la auditoría). La conclusión (hay que fijar la semilla) no cambia; el intervalo sí. Las diapositivas dicen "
             "de 21.10 a 21.15."),
            (2, "El comentario del bloque de `rhohat`: «usa una cuadratura muestreada» (módulo 7)",
             "Lo aleatorio de `rhohat` no es una cuadratura muestreada: es el `jitter = TRUE` por defecto, que añade ruido a los valores de la "
             "covariable en los puntos (ficha de ayuda, sección Randomisation). Con `jitter = FALSE` el resultado es idéntico en cada corrida y no "
             "consume el generador (`recomputo › m7b_jitter`). Las diapositivas dicen el mecanismo correcto y ofrecen `jitter = FALSE`."),
            (2, "«El máximo y el mínimo viven casi siempre en los extremos» (módulo 7)",
             "El módulo 7 dice que el máximo y el mínimo de una curva `rhohat` «viven casi siempre en los extremos, donde apenas hay "
             "puntos». Medido sobre sus tres curvas (`datos › m7.*.rho_max`, `rho_min`, `rho_max_bulto`, `rho_min_bulto`): el mínimo cae "
             "fuera del bulto en las tres; el máximo, solo en la pendiente de `bei` (en la elevación y en la distancia de Bogotá coincide "
             "con el máximo del bulto). Lo que infla la razón es, sobre todo, un mínimo diminuto estimado en la cola. Las diapositivas "
             "dicen lo que se midió."),
            (2, "La pregunta de `rhohat`: el ancho del núcleo también mueve el titular (módulo 7)",
             "La autoevaluación descarta que el 36.1 se deba a un núcleo demasiado estrecho. Con `adjust` (`jitter = FALSE`) la razón total de "
             "Bogotá es 3063 con la mitad del ancho, 36.04 con el defecto, 11.95 con el doble y 2.39 con cuatro veces, y la del bulto, de 2.10 "
             "a 1.11 (`recomputo › m7b_adjust`). La cola infla la razón a cualquier ancho, pero el ancho es parte de la historia. Las "
             "diapositivas lo dicen."),
            (2, "Aclaración: el 1.794e-10 es el condicionamiento de la matriz de diseño, no el de la información de Fisher (módulo 9)",
             "El capítulo lo escribe bien («la matriz de diseño queda con número de condición recíproco 1.794e-10»), pero el texto que sigue "
             "habla de la información de Fisher y se puede leer como si fuera el mismo número. La información tiene un condicionamiento del "
             "orden del cuadrado (2.7e-20, `recomputo › m9b_info`), por debajo de la tolerancia de `solve` (2.2e-16); con 1.794e-10 `solve` "
             "no se quejaría. Las diapositivas distinguen los dos y avisan de los mensajes «Error in solve.default(M)» de la consola."),
            (2, "Las cifras de la envolvente del módulo 10 son de una semilla (62 %, 7.7 %, 38.53854 veces, 3638.23 m)",
             "El módulo 10 las publica con cinco decimales, pero con la semilla 5028 salen 62 radios fuera de 100, 77 de 999 curvas que cruzan "
             "la banda (7.70771 %), 38.53854 veces el nivel puntual y un tramo que acaba en 3638.23 m. Con ocho semillas más "
             "(`recomputo › m10b_sem_1` a `m10b_sem_8`): 64 a 67 radios, de 53 a 78 curvas (5.3 a 7.8 %), 26.5 a 39 veces el nivel, un tramo "
             "que acaba entre 3.76 y 3.93 km, y p del MAD de 0.001 a 0.004. El 0.2 % del nivel puntual no cambia. Las diapositivas dicen "
             "«entre el 5 y el 8 %», «unas 30 veces» y dan el rango de las semillas."),
            (2, "«A menos de 0.64 %» (módulo 10)",
             "El módulo 10 dice que la media de las 999 simulaciones queda «a menos de 0.64 %» de π r² en los 101 nodos. El máximo, sin "
             "redondear, es 0.64499 % con la semilla del capítulo (`datos › m10.mmean_vs_teorica_pct`) y llega a 0.82 % con otras "
             "(`recomputo › m10b_sem_4`). Las diapositivas dicen «a menos de 1 %». Además, son 100 radios informativos (r = 0 vale 0 en las dos curvas)."),
            (2, "«El exceso de parejas está en las escalas cortas y medias; a escala de kilómetros el modelo ya da cuenta» (módulo 10)",
             "La K es acumulada: cuenta todas las parejas a menos de r, de modo que un exceso a escalas cortas la mantiene fuera de la banda a "
             "escalas mayores. Los 3638.23 m son donde la K vuelve a entrar en la banda, no donde acaba el exceso por escala. La g inhomogénea "
             "(`recomputo › m10b_pcf`, 199 simulaciones) sale de su banda sin interrupción hasta 2.2 km y vale 1.20 a 1 km y 1.06 a 2 km. "
             "«Hasta dónde llega lo que el modelo no explica» es, entonces, unos 2 km, y no 3.6 km. Las diapositivas lo dicen así."),
            (2, "«La intensidad variable no explica la agregación» (módulo 10): se probó un plano, no «la intensidad variable»",
             "La envolvente del módulo 10 es la de `ppm(~ xc + yc)`: un plano log-lineal en x e y (3 parámetros). Con una tendencia polinómica "
             "más flexible (`recomputo › m10b_flex`) los tests globales dejan de rechazar: grado 10 (66 parámetros), DCLF p = 0.055 y MAD "
             "0.215; grado 12 (91 parámetros), DCLF 0.135 a 0.22 y MAD 0.345 a 0.415 (199 simulaciones). Esa curva llega a 208 sedes por km² "
             "y a casi cero en otros sitios: imita los grupos con la tendencia, y con un solo patrón tendencia y agrupación no se separan. "
             "El exceso por debajo de unos 2 km sobrevive (de 32 a 43 % de los radios siguen fuera). Las diapositivas acotan el veredicto a "
             "«un plano en x e y» y lo explican."),
            (2, "«Comparten manzana, predio y edificio» (módulo 10)",
             "Es la explicación del capítulo para la agregación y no se comprobó con datos de predios. Lo medido (`recomputo › m11b_dups`): hay "
             "79 sedes que comparten sitio exacto (39 sitios) y el 29.8 % de las sedes tiene otra a menos de 100 m, contra 16.3 % (sd 1.2) en 99 "
             "patrones simulados del modelo con tendencia. Las diapositivas la dan como explicación plausible no comprobada."),
            (2, "«Tres verosimilitudes distintas tardan lo mismo» (módulo 11)",
             "`kppm` ajusta por contraste mínimo (`method = \"mincon\"`, el defecto, según la ayuda), y no evalúa ninguna verosimilitud; el "
             "propio capítulo lo dice un párrafo después. Tardan lo mismo porque el contraste solo evalúa su K teórica, que es barata: lo que se "
             "paga es estimar la K isotrópica (`Kest` isotrópica tarda casi todo el tiempo del ajuste, `recomputo › m11b_kemp`). Las "
             "diapositivas lo dicen así."),
            (2, "«El valle que el contraste mínimo está minimizando es casi plano» (módulo 11)",
             "No se sostiene (`recomputo › m11b_valle`): evaluado cada contraste en los parámetros del otro ajuste, sube 178 % y 195 % sobre su "
             "mínimo, y con κ reoptimizado el de traslación sube 57 % en σ = 932 m: cada K empírica tiene su propio mínimo bien marcado. Lo que "
             "ocurre es otra cosa: κσ² (lo que fija la K a r corto) es casi igual (0.183 y 0.190), por eso las dos K coinciden hasta 1 km, pero κ "
             "lo fija el exceso K − π r² a r grande, una resta de números grandes: la K isotrópica queda hasta 5.5 % por debajo de la de traslación "
             "y 1/κ cambia ×1.93. Las diapositivas dan esta explicación."),
            (2, "«40 sitios con sedes repetidas» (módulo 11)",
             "Son 40 sedes sobrantes en 39 sitios: 38 sitios con dos sedes y 1 con tres, 79 sedes implicadas (`recomputo › m11b_dups`). Las "
             "diapositivas dicen «40 sedes repetidas»."),
            (2, "El μ de `kppm` hereda el +0.33 % del `ppm` forzado (módulo 11)",
             "`kppm` ajusta por dentro un `ppm` con `forcefit = TRUE` y calcula μ = λ̂ / κ con ese λ̂: κ · μ = 5.7121 sedes por km², no 5.6932. Con "
             "n / |W| serían 27.0 y 52.2, y no 27.1 y 52.3. Las diapositivas conservan lo que devuelve `kppm` y lo advierten en las notas."),
            (2, "Los errores estándar de `vcov(kppm)` usan una aproximación rápida (módulo 11)",
             "Con una cuadratura de 6247 puntos `vcov` da lo mismo que `fast = TRUE`, que la ayuda dice que subestima las varianzas. Con "
             "`fast = FALSE` el efecto de diseño es 26.1 y no 26.03409, y las 2 107 sedes valen 80.6 y no 80.93235 (`recomputo › m11b_vcov`). "
             "Las diapositivas dicen «unas 26» y «unas 80»."),
            (2, "El índice de dispersión del Hawkes no tiene cinco decimales (módulo 11)",
             "El 5.15454 es de una simulación y de 200 intervalos de 20 unidades: con 200 réplicas el índice tiene media 5.04 y desviación 0.57, "
             "y para la misma simulación va de 9.9 con 20 intervalos a 2.9 con 2000 (`recomputo › m11b_hawkes`). «5.4 veces más agregado» es de esa "
             "simulación. Las diapositivas dan 5.15 y 0.96, el tamaño del intervalo y el rango entre réplicas."),
            (2, "Los kppm con tendencia no son los de `~ 1` (módulo 11)",
             "La tabla de errores estándar usa `kppm(~ xc + yc)`, que ajusta la K inhomogénea: sus parámetros de grupo cambian (Thomas con K de "
             "traslación, κ = 1.59e-07 y σ = 1067 m, contra 1.09e-07 y 1320 m con `~ 1`; `recomputo › m11b_trend`). El capítulo no lo dice. "
             "Las notas de las diapositivas sí."),
            (2, "Los tiempos del módulo 11 dependen de la máquina",
             "El capítulo publica 126.5 s contra 0.47 s para Thomas; al volver a ajustar aquí salen 128.8 s contra 0.48 s, y el cociente, "
             "267.3 contra el 267.52220 del JSON. No es un error: son mediciones de tiempo. Se aceptan con tolerancia (MEDIDA) y las "
             "diapositivas dicen que los tiempos dependen de la máquina y «unas 270 veces»."),
        ])

        # ---- portada y presupuesto de minutos ----
        REG("90", P("duración de la clase pedida por el docente (90 min), decisión D1; no es un dato del capítulo"), en=("Portada", "De estimar a modelar"))
        REG(["12", "20", "14", "17", "5"], P("minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo"), en=DIVISORES, cx=r"\d min")
        REG("6", P("minutos de la apertura (portada, hoja de ruta, tesis y ejemplo): decisión del docente, no un dato del capítulo"), en=("De estimar a modelar",), cx=r"6 min")
        REG("86", A(lambda: 6 + 12 + 20 + 12 + 14 + 17 + 5, "suma de los minutos asignados a los bloques de la sesión"), en=("De estimar a modelar",), cx=r"Suman 86")
        REG("4", A(lambda: 90 - (6 + 12 + 20 + 12 + 14 + 17 + 5), "los 90 min menos los 86 asignados"), en=("De estimar a modelar",), cx=r"los 4 restantes")

        # ---- la tesis y los cinco resultados ----
        REG("36.1", RJ("m7.bogota.curva.razon", "m7.bogota.total"))
        REG("1.58", RJ("m7.bogota.curva.razon_bulto", "m7.bogota.bulto"))
        REG("9.2", RJ("m8.cuadratura.rango_aic", "m8_nd.rango_aic"))
        REG("0.2", RJ("m10.nivel_puntual_pct", "m10.nivel_puntual_pct"))
        REG("7.7", RJ("m10.tasa_salida.pct", "m10.nativa.pct"))
        REG("27.1", RJ("m11.ajustes[0].mu", "m11_Thomas.iso.mu"))
        REG("52.3", RJ("m11.ajustes[1].mu", "m11_Thomas.translate.mu"))

        # ---- módulo 7 · covariables ----
        REG("3604", RJ("m7.bei.n", "m7.bei.n"))
        REG("3605", E("m7.bei.ayuda", "3605 trees"))
        REG("1000", Rr("m7.bei.ventana_x_m"), en=("`rhohat` dibuja",), cx=r"1000 m por")
        REG("500", Rr("m7.bei.ventana_y_m"), en=("`rhohat` dibuja",), cx=r"por 500")
        REG("119.81", Rr("m7.bei.elevacion_min_m"))
        REG("159.48", Rr("m7.bei.elevacion_max_m"))
        REG("5", P("percentil inferior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95)"), cx=r"percentiles? 5")
        REG("95", P("percentil superior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95)"), cx=r"percentiles? 5 y 95|percentil 5 al 95|5 y 95|5 al 95")
        REG("22.8", RJ("m7.bogota.curva.cola_infla", "m7.bogota.infla"))
        REG("3063", Rr("m7b_adjust.total[0]"), en=("La curva `rhohat` de Bogotá sube",))
        REG("2.39", Rr("m7b_adjust.total[3]"), en=("La curva `rhohat` de Bogotá sube",))
        REG("2.10", Rr("m7b_adjust.bulto[0]"), en=("La curva `rhohat` de Bogotá sube",))
        REG("1.11", Rr("m7b_adjust.bulto[3]"), en=("La curva `rhohat` de Bogotá sube",))
        REG("36", RJ("m7.bogota.curva.razon", "m7.bogota.total"), cx=r"razón de 36")
        REG("9.0", RJ("m7.bei.elevacion.cola_infla", "m7.elevacion.infla"))
        REG("2.5", RJ("m7.bei.pendiente.cola_infla", "m7.pendiente.infla"))
        REG("2.36", RJ("m7.bei.elevacion.razon_bulto", "m7.elevacion.bulto"))
        REG("3.34", RJ("m7.bei.pendiente.razon_bulto", "m7.pendiente.bulto"))
        REG("20", Rr("m7_semillas.n_semillas"), cx=r"20 semillas")
        REG("21.10", Rr("m7_semillas.min"))
        REG("21.15", Rr("m7_semillas.max"))
        REG(["21.12", "21.14"], T("entre 21.12 y 21.14"))

        # ---- módulo 8 · el Poisson inhomogéneo ----
        REG("7.44e-16", RJ("m8.homogeneo.dif_relativa", "m8_homogeneo.dif_relativa"))
        REG("5.6932", RJ("m8.homogeneo.lambda_km2", "m8_homogeneo.lambda_km2"))
        REG("5.69321", RJ("m8.homogeneo.lambda_km2", "m8_homogeneo.lambda_km2"))
        REG("5.71211", RJ("m8.forzado.lambda_km2", "m8_homogeneo.forzado.lambda_km2"))
        REG("0.33", RJ("m8.forzado.exceso_pct", "m8_homogeneo.forzado.exceso_pct"))
        REG("368.86563", RJ("m8.forzado.suma_pesos_km2", "m8_homogeneo.forzado.suma_pesos_km2"))
        REG("370.08982", RJ("m8.forzado.area_km2", "m8_homogeneo.area_km2"))
        REG("4140", RJ("m8.cuadratura.defecto_ficticios", "m8_nd.ficticios_por_defecto"))
        REG("100", J("m8.cuadratura.defecto_nd"), cx=r"= 100|^\|")
        REG("2107", RJ("m5.capas.oferta.n", "urbana.n_urbana"))
        REG("1.22418", RJ("m8.cuadratura.tabla[1].sin_contar_km2", "m8_homogeneo.forzado.faltan_km2"))
        REG("201", RJ("m8.cuadratura.tabla[1].teselas_vacias", "m8_homogeneo.forzado.teselas_vacias"))
        REG("4345", RJ("m8.cuadratura.tabla[1].teselas_tocan", "m8_homogeneo.forzado.teselas_tocan"))
        REG("100x100", [J("m8.cuadratura.tabla[1].rejilla_pesos"), Rr("m8_homogeneo.ntile")])
        REG("200x200", [J("m8.cuadratura.tabla[1].pixeles"), Rr("m8_homogeneo.npix")])
        REG("235", Rr("m8_homogeneo.tesela_m[0]"))
        REG("400", Rr("m8_homogeneo.tesela_m[1]"))
        REG("100", J("m8.cuadratura.tabla[1].rejilla_pesos"), en=("La cuadratura deja sin contar",), cx=r"entre 100 en cada eje")
        for i, nd in ((0, "50"), (2, "200"), (3, "300")):
            REG(nd, J(f"m8.cuadratura.tabla[{i}].nd"))
        REG("100", J("m8.cuadratura.tabla[1].nd"), en=("Un modelo, cuatro cuadraturas",))
        REG("1099", RJ("m8.cuadratura.tabla[0].ficticios", "m8_nd.filas[0].ficticios"))
        REG("15764", RJ("m8.cuadratura.tabla[2].ficticios", "m8_nd.filas[2].ficticios"))
        REG("35495", RJ("m8.cuadratura.tabla[3].ficticios", "m8_nd.filas[3].ficticios"))
        REG("0.75800", RJ("m8.cuadratura.tabla[0].sin_contar_km2", "m8_nd.filas[0].sin_contar_km2"))
        REG("0.38996", RJ("m8.cuadratura.tabla[3].sin_contar_km2", "m8_nd.filas[3].sin_contar_km2"))
        REG("55097.08", RJ("m8.cuadratura.tabla[0].aic", "m8_nd.filas[0].aic"))
        REG("55091.81", RJ("m8.cuadratura.tabla[1].aic", "m8_nd.filas[1].aic"))
        REG("55091.80", RJ("m8.cuadratura.tabla[2].aic", "m8_nd.filas[2].aic"))
        REG("55101.00", RJ("m8.cuadratura.tabla[3].aic", "m8_nd.filas[3].aic"))
        REG("-27546.54", RJ("m8.cuadratura.tabla[0].logver_ppm", "m8_nd.filas[0].logver_ppm"))
        REG("-27543.91", RJ("m8.cuadratura.tabla[1].logver_ppm", "m8_nd.filas[1].logver_ppm"))
        REG("-27543.90", RJ("m8.cuadratura.tabla[2].logver_ppm", "m8_nd.filas[2].logver_ppm"))
        REG("-27548.50", RJ("m8.cuadratura.tabla[3].logver_ppm", "m8_nd.filas[3].logver_ppm"))
        REG("-27550.65", RJ("m8.cuadratura.tabla[0].logver_exacta", "m8_nd.filas[0].logver_exacta"))
        REG("-27550.66", LJ(["m8.cuadratura.tabla[1].logver_exacta", "m8.cuadratura.tabla[2].logver_exacta"], ["m8_nd.filas[1].logver_exacta", "m8_nd.filas[2].logver_exacta"]))
        REG("-27550.64", RJ("m8.cuadratura.tabla[3].logver_exacta", "m8_nd.filas[3].logver_exacta"))
        REG("0.12895", RJ("m8.cuadratura.rango_pendiente_en_ee", "m8_nd.rango_pendiente_en_ee"))
        REG("4.59973", RJ("m8.cuadratura.rango_logver_ppm", "m8_nd.rango_logver_ppm"))
        REG("0.03", RJ("m8.cuadratura.rango_logver_exacta", "m8_nd.rango_logver_exacta"))
        REG("2113.76", RJ("m8.cuadratura.tabla[1].integral_exacta", "m8_nd.filas[1].sedes_esperadas"))
        REG("13.44572", RJ("m8.comparacion.gana_distancia_ppm", "m8_nd.gana_distancia_ppm"))
        REG("13.4", RJ("m8.comparacion.gana_distancia_ppm", "m8_nd.gana_distancia_ppm"))
        REG("0.07", RJ("m8.comparacion.gana_constante_exacta", "m8_nd.gana_constante_exacta"))
        REG("0.51644", RJ("m8.comparacion.gana_constante_misma", "m8_nd.gana_constante_misma"))

        # ---- módulo 9 · ppm ----
        REG("9377", T("EPSG:9377"))
        REG("1.794e-10", RJ("m9.crudo.cond_reciproco", "m9.crudo.cond"))
        REG("2.7e-20", Rr("m9b_info.rcond_info_crudo"))
        REG("2.2e-16", Rr("m9b_info.tolerancia_solve"))
        REG("0.1178", RJ("m9.centrado.cond_reciproco", "m9.centrado.cond"))
        REG("0x0", Rr("m9.crudo.dim_sqrt_diag_null"))
        REG("117.038", RJ("m9.crudo.coef[0]", "m9.crudo.coef[0]"))
        REG("4900000", T("4 900 000 unidades"))
        REG("6.567e+08", RJ("m9.mejora_condicion", "m9.mejora_condicion"))
        REG("6.566e+08", A(lambda: 0.1178 / 1.794e-10, "0.1178 / 1.794e-10 con las cifras redondeadas"))
        REG("55055.1", RJ("m9.centrado.aic", "m9.centrado.aic"))
        REG("-0.0242564", RJ("m9.centrado.coef[1]", "m9.centrado.coef[1]"))
        REG("0.00503338", RJ("m9.centrado.ee[1]", "m9.centrado.ee[1]"))
        REG("-4.82", RJ("m9.centrado.z[1]", "m9.centrado.z[1]"))
        REG("-0.00521978", RJ("m9.centrado.coef[2]", "m9.centrado.coef[2]"))
        REG("0.00306347", RJ("m9.centrado.ee[2]", "m9.centrado.ee[2]"))
        REG("-1.70", RJ("m9.centrado.z[2]", "m9.centrado.z[2]"))
        REG("-6.6091e-06", RJ("m9.distancia.coef[1]", "m9.distancia.coef[1]"))
        REG("5.4394e-06", RJ("m9.distancia.ee[1]", "m9.distancia.ee[1]"))
        REG("-1.22", RJ("m9.distancia.z[1]", "m9.distancia.z[1]"), en=("Habría evidencia", "Para la misma distancia"))
        REG("1.96", J("m11.tendencia.z_critico"))

        # ---- módulo 10 · diagnóstico ----
        REG("999", RJ("m10.nsim", "m10.nsim"))
        REG("39", A(lambda: round(2 / r("m10_e39.nivel_puntual") - 1), "nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1)"))
        REG("101", RJ("m10.n_nodos", "m10.n_nodos"))
        REG("0.65", A(lambda: 0.65 if r("m10.mmean_vs_teorica_pct") < 0.65 else -1, "el máximo de |media − π r²| / π r² (0.64499 %) es menor que 0.65 %"), cx=r"menos de 0\.65")
        REG("0.64", T("a menos de 0.64 %"))
        REG("0.64499", RJ("m10.mmean_vs_teorica_pct", "m10.mmean_vs_teorica_pct"))
        REG("0.025", [Rr("m10_e39.dclf"), Rr("m10_e39.mad")])
        REG("0.0500", Rr("m10_e39.nivel_puntual"))
        REG("78.5156", Rr("m10_e39.pct_fuera"))
        REG("5", A(lambda: 100 * r("m10_e39.nivel_puntual"), "100 × el nivel puntual de la envolvente de 39 (0.05)"), cx=r"5 % de una envolvente")
        REG("62", RJ("m10.pct_r_fuera_de_banda", "m10.pct_fuera"), cx=r"62 %|62 de los")
        REG("62", Rr("m11_redwood.n"), cx=r"62 puntos|62 plántulas")
        REG("100", J("m10.tasa_salida.nodos_r_simulador"), cx=r"de los 100 radios")
        REG("58.68", RJ("m10.primer_r_fuera_m", "m10.primer_r_fuera_m"))
        REG("3638.23", RJ("m10.ultimo_r_fuera_m", "m10.ultimo_r_fuera_m"))
        REG("38", RJ("m10.nodos_dentro_tras_el_tramo", "m10.nodos_dentro_tras_el_tramo"))
        REG("5868.12", RJ("m10.r_max_m", "m10.r_max_m"))
        REG("77", RJ("m10.tasa_salida.fuera", "m10.nativa.fuera"))
        REG("7.70771", RJ("m10.tasa_salida.pct", "m10.nativa.pct"))
        REG("38.53854", RJ("m10.tasa_salida.veces_el_nivel", "m10.veces_el_nivel"))
        REG(["0.001", "0.00100"], RJ("m10.test_global.dclf_p", "m10.dclf_p"))
        REG("0.00400", RJ("m10.test_global.mad_p", "m10.mad_p"))
        REG("512", RJ("m10.tasa_salida.nodos_r", "m10.nativa.nodos"))
        REG("1959.86", RJ("m10.test_global.r_mad_observada_m", "m10.r_mad_observada_m"))
        REG("5650.35", RJ("m10.test_global.r_min_mad_superan_m", "m10.r_min_mad_superan_m"))
        REG("40", J("m11.duplicados.repetidos"))
        REG("6.2", J("m11.duplicados.cambio_maximo_pct"))

        # ---- módulo 11 · conglomerados ----
        REG("127", A(lambda: sum(d(f"m11.ajustes[{i}].segundos") for i in (0, 2, 4)) / 3, "promedio de los tres tiempos con K isotrópica del capítulo (126.5, 126.7 y 127.1 s)"))
        for tok, i, mod, c in (("932", 0, "Thomas", "iso"), ("1320", 1, "Thomas", "translate"), ("1782", 2, "MatClust", "iso"),
                               ("2522", 3, "MatClust", "translate"), ("1296", 4, "LGCP", "iso"), ("1927", 5, "LGCP", "translate")):
            REG(tok, RJ(f"m11.ajustes[{i}].parametros.scale", f"m11_{mod}.{c}.parametros.scale"))
        for tok, i, mod, c, tol in (("126.5", 0, "Thomas", "iso", 5), ("0.47", 1, "Thomas", "translate", 0.5), ("126.7", 2, "MatClust", "iso", 5),
                                    ("0.43", 3, "MatClust", "translate", 0.5), ("127.1", 4, "LGCP", "iso", 5), ("0.88", 5, "LGCP", "translate", 0.5)):
            REG(tok, [J(f"m11.ajustes[{i}].segundos"), M(f"m11_{mod}.{c}.segundos", tol)])
        REG("267.52220", [J("m11.divergencia[0].veces_mas_rapido"),
                          Spec("medida", "recomputo › m11_Thomas.iso.segundos / m11_Thomas.translate.segundos (±5, depende de la máquina)",
                               [("cociente de los dos tiempos recalculados", lambda: r("m11_Thomas.iso.segundos") / r("m11_Thomas.translate.segundos"))], tol=5)])
        REG("200", [A(lambda: 200 if d("m11.divergencia[0].veces_mas_rapido") > 200 else -1, "el cociente de tiempos del capítulo (267.52220) es mayor que 200"),
                    Spec("medida", "recomputo › m11_Thomas.iso.segundos / m11_Thomas.translate.segundos, a la decena (±5, depende de la máquina)",
                         [("200 si el cociente de los dos tiempos recalculados supera 200", lambda: 200 if r("m11_Thomas.iso.segundos") / r("m11_Thomas.translate.segundos") > 200 else -1)], tol=0)],
            cx=r"más de 200 veces")
        REG("555", J4("m10.coste.veces_isotropica_sobre_traslacion"))
        REG("129", A(lambda: r("m11_Thomas.iso.segundos"), "segundos del ajuste de Thomas con K isotrópica en esta máquina (128.8)"))
        REG("48.2", RA("m11.divergencia[0].parametros.kappa", lambda: 100 * (1 - r("m11_Thomas.translate.parametros.kappa") / r("m11_Thomas.iso.parametros.kappa")), "100 × (1 − κ de traslación / κ isotrópica)"))
        REG("41.6", RA("m11.divergencia[0].parametros.scale", lambda: 100 * (r("m11_Thomas.translate.parametros.scale") / r("m11_Thomas.iso.parametros.scale") - 1), "100 × (escala de traslación / escala isotrópica − 1)"))
        REG("93.2", RA("m11.divergencia[0].mu_pct", lambda: 100 * (r("m11_Thomas.translate.mu") / r("m11_Thomas.iso.mu") - 1), "100 × (μ de traslación / μ isotrópica − 1)"))
        REG("22", Rr("m11_ventana.piezas"))
        REG("2.63", [Rr("m11_redwood.iso.mu"), T("μ = 2.63 contra 3.27")])
        REG("3.27", [Rr("m11_redwood.translate.mu"), T("μ = 2.63 contra 3.27")])
        REG("24.0", [A(lambda: 100 * (r("m11_redwood.translate.mu") / r("m11_redwood.iso.mu") - 1), "100 × (μ de traslación / μ isotrópica − 1) en redwood"), T("un 24.0 %")])

        def kth(rr, kappa, esc):
            return math.pi * rr ** 2 + (1 - math.exp(-rr ** 2 / (4 * esc ** 2))) / kappa

        def kdif(rr):
            ka, ea = r("m11_Thomas.iso.parametros.kappa"), r("m11_Thomas.iso.parametros.scale")
            kb, eb = r("m11_Thomas.translate.parametros.kappa"), r("m11_Thomas.translate.parametros.scale")
            return 100 * abs(kth(rr, kb, eb) - kth(rr, ka, ea)) / kth(rr, ka, ea)

        for tok, rr in (("0.6", 500), ("0.9", 1000), ("4.8", 2000)):
            REG(tok, A(lambda rr=rr: kdif(rr), f"diferencia relativa de la K de Thomas con los dos juegos de parámetros a {rr} m (forma cerrada)"), en=("Dos conglomerados distintos",))
        REG(["500", "1000", "2000"], T("(500.0, 1000.0, 2000.0)"), en=("Dos conglomerados distintos",))
        REG("1373", RJ("m11.duplicados.efecto[0].sin_duplicados.scale", "m11_Thomas.sin_duplicados.parametros.scale"))
        REG("4.0", RA("m11.duplicados.efecto[0].cambio_pct.scale", lambda: 100 * (r("m11_Thomas.sin_duplicados.parametros.scale") / r("m11_Thomas.translate.parametros.scale") - 1), "100 × (escala sin duplicados / escala con duplicados − 1), Thomas con K de traslación"))
        REG("4", P("constante de la forma cerrada de la K de Thomas: π r² + (1 − exp(−r²/(4 σ²)))/κ"), cx=r"4 σ|4 κ σ")
        REG("3", T("decisión 3 de aquel capítulo"), cx=r"decisión 3")

        # la tabla de los errores estándar con conglomerados (el z y la inflación del coeficiente de xc)
        def tend(mod, c, k, i=1):
            return r(f"m11_{mod}.tendencia.{c}.{k}[{i}]")
        REG("0.0199411", RJ("m11.tendencia.ajustes[0].ee[0]", "m11_Thomas.tendencia.iso.ee[1]"))
        REG("0.0256821", RJ("m11.tendencia.ajustes[1].ee[0]", "m11_Thomas.tendencia.translate.ee[1]"))
        REG("0.0199819", RJ("m11.tendencia.ajustes[2].ee[0]", "m11_MatClust.tendencia.iso.ee[1]"))
        REG("0.0258419", RJ("m11.tendencia.ajustes[3].ee[0]", "m11_MatClust.tendencia.translate.ee[1]"))
        REG("0.0209735", RJ("m11.tendencia.ajustes[4].ee[0]", "m11_LGCP.tendencia.iso.ee[1]"))
        REG("0.026767", RJ("m11.tendencia.ajustes[5].ee[0]", "m11_LGCP.tendencia.translate.ee[1]"))
        REG("-1.22", RJ("m11.tendencia.ajustes[0].z[0]", "m11_Thomas.tendencia.iso.z[1]"), en=("Con conglomerados",))
        REG("-0.94", LJ(["m11.tendencia.ajustes[1].z[0]", "m11.tendencia.ajustes[3].z[0]"], ["m11_Thomas.tendencia.translate.z[1]", "m11_MatClust.tendencia.translate.z[1]"]))
        REG("-1.21", RJ("m11.tendencia.ajustes[2].z[0]", "m11_MatClust.tendencia.iso.z[1]"))
        REG("-1.16", RJ("m11.tendencia.ajustes[4].z[0]", "m11_LGCP.tendencia.iso.z[1]"))
        REG("-0.91", RJ("m11.tendencia.ajustes[5].z[0]", "m11_LGCP.tendencia.translate.z[1]"))
        REG("3.96", RJ("m11.tendencia.ajustes[0].inflacion[0]", "m11_Thomas.tendencia.iso.inflacion[1]"))
        REG("5.10", RJ("m11.tendencia.ajustes[1].inflacion[0]", "m11_Thomas.tendencia.translate.inflacion[1]"))
        REG("3.97", RJ("m11.tendencia.ajustes[2].inflacion[0]", "m11_MatClust.tendencia.iso.inflacion[1]"))
        REG("5.13", RJ("m11.tendencia.ajustes[3].inflacion[0]", "m11_MatClust.tendencia.translate.inflacion[1]"))
        REG("4.17", RJ("m11.tendencia.ajustes[4].inflacion[0]", "m11_LGCP.tendencia.iso.inflacion[1]"))
        REG("5.32", RJ("m11.tendencia.ajustes[5].inflacion[0]", "m11_LGCP.tendencia.translate.inflacion[1]"))
        REG("1.22", RA("m11.tendencia.z_xc_abs_max", lambda: max(abs(tend(mm, c, "z")) for mm in MODELOS for c in ("iso", "translate")), "máximo de |z| del coeficiente de xc en los seis ajustes"), en=("Con conglomerados",))
        REG("3.96177", RA("m11.tendencia.inflacion_xc_min", lambda: min(tend(mm, c, "inflacion") for mm in MODELOS for c in ("iso", "translate")), "mínimo de la inflación del error estándar de xc en los seis ajustes"))
        REG("5.31788", RA("m11.tendencia.inflacion_xc_max", lambda: max(tend(mm, c, "inflacion") for mm in MODELOS for c in ("iso", "translate")), "máximo de la inflación del error estándar de xc en los seis ajustes"))
        REG("1.21640", RA("m11.tendencia.z_xc_abs_max", lambda: max(abs(tend(mm, c, "z")) for mm in MODELOS for c in ("iso", "translate")), "máximo de |z| del coeficiente de xc en los seis ajustes"))
        REG("26.03409", RA("m11.tendencia.efecto_diseno", lambda: tend("Thomas", "translate", "inflacion") ** 2, "inflación del error estándar de xc con Thomas y K de traslación, al cuadrado"))
        REG("80.93235", RA("m11.tendencia.n_efectivo", lambda: d("m11.tendencia.n") / tend("Thomas", "translate", "inflacion") ** 2, "n / efecto de diseño"))

        # Hawkes
        REG("150", P("las primeras 150 unidades de tiempo que muestra la figura (decisión de la figura propia)"))
        REG("0.5", Rr("m11_hawkes.mu"))
        REG("0.8", Rr("m11_hawkes.alpha"))
        REG("1.4", Rr("m11_hawkes.beta"))
        REG("0.5714", RJ("m11.hawkes.razon_ramificacion", "m11_hawkes.razon_ramificacion"))
        REG(["1.1667", "1.16667"], RJ("m11.hawkes.tasa_teorica", "m11_hawkes.tasa_teorica"))
        REG("1.14425", RJ("m11.hawkes.tasa_simulada", "m11_hawkes.tasa_simulada"))
        REG("4577", RJ("m11.hawkes.n_eventos", "m11_hawkes.n_eventos"))
        REG("5.15454", RJ("m11.hawkes.dispersion_hawkes", "m11_hawkes.dispersion_hawkes"))
        REG("0.95789", RJ("m11.hawkes.dispersion_poisson", "m11_hawkes.dispersion_poisson"))
        REG("5.4", RJ("m11.hawkes.veces_mas_agregado", "m11_hawkes.veces_mas_agregado"))
        REG("5030", J("meta.semillas.hawkes"))

        # ---- el proyecto integrador ----
        REG("2209", Rr("urbana.n_capa"))
        REG("12.25", T("versión 12.25", corpus="fuentes"))
        REG("370.09", Rr("urbana.area_km2"))
        REG("5.69", [Rr("urbana.lambda_km2"), T("5.6932")])
        REG("66.3", RJ("m2.familia.caida_pct", "anchos.caida_pct"))
        REG("233", RJ("m2.familia.sigmas_m[0]", "anchos.sigmas_m[0]"))
        REG("1867", RJ("m2.familia.sigmas_m[6]", "anchos.sigmas_m[6]"))
        REG("800", J("m4.sigmas_m"))
        REG("270.36", RJ("m4.tabla[2].masa_defecto", "bordes.800.masa_defecto"))
        REG("262.00", RJ("m4.tabla[2].masa_diggle", "bordes.800.masa_diggle"))


        # ---- revisión tras la auditoría B (1 oct 2026): números nuevos y cifras que dejan de ser de una sola semilla ----
        SEM = list(range(1, 9))                                       # las ocho semillas nuevas de la envolvente de 999

        def sem(campo):
            return [r(f"m10b_sem_{k}.{campo}") for k in SEM]

        def con_cap(campo, ruta_cap):                                  # las ocho nuevas y la del capítulo
            return sem(campo) + [r(ruta_cap)]

        def mediana(xs):
            xs = sorted(xs)
            n = len(xs)
            return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2

        # la banda entera cruza entre el 5 y el 8 % (nueve semillas), de 53 a 78 curvas, unas 30 veces el nivel puntual
        REG("5", A(lambda: math.floor(min(con_cap("tasa_pct_nativa", "m10.nativa.pct"))), "mínimo de la tasa de salida de la banda entera con nueve semillas (5.31 %), hacia abajo"), cx=r"entre el 5 y el 8|5–8")
        REG("8", A(lambda: math.ceil(max(con_cap("tasa_pct_nativa", "m10.nativa.pct"))), "máximo de la tasa de salida de la banda entera con nueve semillas (7.81 %), hacia arriba"), cx=r"entre el 5 y el 8|5–8")
        REG("53", A(lambda: min(con_cap("tasa_fuera_nativa", "m10.nativa.fuera")), "mínimo de curvas que cruzan la banda de las otras, con nueve semillas"), cx=r"53 y 78|53 a 78")
        REG("78", A(lambda: max(con_cap("tasa_fuera_nativa", "m10.nativa.fuera")), "máximo de curvas que cruzan la banda de las otras, con nueve semillas"), cx=r"53 y 78|53 a 78")
        REG("5.3", A(lambda: round(min(con_cap("tasa_pct_nativa", "m10.nativa.pct")), 1), "mínimo de la tasa de salida (%) con nueve semillas"), cx=r"5\.3 al 7\.8")
        REG("7.8", A(lambda: round(max(con_cap("tasa_pct_nativa", "m10.nativa.pct")), 1), "máximo de la tasa de salida (%) con nueve semillas"), cx=r"5\.3 al 7\.8")
        REG("30", A(lambda: round(mediana(con_cap("veces_el_nivel_nativa", "m10.veces_el_nivel")) / 10) * 10, "mediana (32.0) de las veces que la banda entera supera el nivel puntual, con nueve semillas, a la decena"), cx=r"unas 30 veces")
        REG("26.5", A(lambda: round(min(con_cap("veces_el_nivel_nativa", "m10.veces_el_nivel")), 1), "mínimo de las veces el nivel puntual con nueve semillas"), cx=r"26\.5 a 39")
        REG("39", A(lambda: round(max(con_cap("veces_el_nivel_nativa", "m10.veces_el_nivel"))), "máximo de las veces el nivel puntual con nueve semillas"), cx=r"26\.5 a 39")
        REG("0.004", A(lambda: max(con_cap("mad_p", "m10.mad_p")), "máximo del p del MAD con nueve semillas"), cx=r"0\.001 a 0\.004")
        REG("0.001", A(lambda: min(con_cap("mad_p", "m10.mad_p")), "mínimo del p del MAD con nueve semillas"), cx=r"0\.001 a 0\.004")
        REG("4.30430", Rr("m10.simulador.pct"))
        REG("100", Rr("m10.simulador.nodos"), cx=r"los 100 radios|100 radios informativos")
        # la fracción de radios fuera y hasta dónde llega el tramo
        REG("62", A(lambda: min(con_cap("pct_101", "m10.pct_fuera")), "mínimo de radios fuera de 100 con nueve semillas"), cx=r"de 62 a 67")
        REG("67", A(lambda: max(con_cap("pct_101", "m10.pct_fuera")), "máximo de radios fuera de 100 con nueve semillas"), cx=r"de 62 a 67")
        REG("64", A(lambda: min(sem("pct_101")), "mínimo de radios fuera de 100 con las ocho semillas nuevas"), cx=r"de 64 a 67")
        REG("67", A(lambda: max(sem("pct_101")), "máximo de radios fuera de 100 con las ocho semillas nuevas"), cx=r"de 64 a 67")
        REG("3.6", A(lambda: round(min(con_cap("ultimo_r_101", "m10.ultimo_r_fuera_m")) / 1000, 1), "último radio fuera (km), mínimo con nueve semillas"), cx=r"3\.6–3\.9")
        REG("3.9", A(lambda: round(max(con_cap("ultimo_r_101", "m10.ultimo_r_fuera_m")) / 1000, 1), "último radio fuera (km), máximo con nueve semillas"), cx=r"3\.6–3\.9")
        REG("3.8", A(lambda: round(min(sem("ultimo_r_101")) / 1000, 1), "último radio fuera (km), mínimo con las ocho semillas nuevas"), cx=r"3\.8 y 3\.9")
        REG("3.9", A(lambda: round(max(sem("ultimo_r_101")) / 1000, 1), "último radio fuera (km), máximo con las ocho semillas nuevas"), cx=r"3\.8 y 3\.9")
        REG("0.82", A(lambda: round(max(sem("max_rel_mmean_101_pct")), 2), "máximo de |media − π r²| / π r² (%) con las ocho semillas nuevas"), cx=r"llega a 0\.82")
        REG("1", A(lambda: 1 if max(con_cap("max_rel_mmean_101_pct", "m10.mmean_vs_teorica_pct")) < 1 else -1, "el máximo de |media − π r²| / π r² con nueve semillas (0.82 %) es menor que 1 %"), cx=r"menos de 1 %")
        # la g inhomogénea mira cada escala por separado
        REG("11.46", A(lambda: d("m10.r_max_m") / d("m10.tasa_salida.nodos_r"), "primer radio no nulo de la rejilla nativa: r máximo (5868.12 m) entre los 512 radios no nulos"))
        REG("56.4", Rr("m9b_dcen.dif_aic"))
        REG("3", Rr("m9b_dcen.k_cuadratico"), cx=r"cuadrático \(3 parámetros")
        REG("199", Rr("m10b_pcf.nsim"))
        REG("2.2", A(lambda: round(r("m10b_pcf.primera_racha_hasta_r") / 1000, 1), "hasta dónde llega la primera racha de radios fuera de la banda de la g inhomogénea (km)"))
        REG("1.20", Rr("m10b_pcf.g_1000.g_obs"))
        REG("1.06", Rr("m10b_pcf.g_2000.g_obs"))
        REG("1", P("distancia de 1 km a la que se lee la g inhomogénea (decisión de la lectura)"), cx=r"a 1 km|hasta 1 km")
        REG("2", A(lambda: round(r("m10b_pcf.primera_racha_hasta_r") / 1000), "la primera racha de la g inhomogénea fuera de su banda llega a 2.2 km ≈ 2 km"), cx=r"a 2 km|unos 2 km")
        REG("2", A(lambda: round(r("m11b_kemp.r_dif_max_m") / 1000), "radio de la mayor diferencia entre las dos K empíricas (2269 m ≈ 2 km)"), cx=r"unos 2 km")
        # el nivel de confianza de las bandas de rhohat
        REG("95", E("ayuda_b.rhohat", "confidence=0.95"), cx=r"confianza del 95")
        # una tendencia más flexible
        REG("12", Rr("m10b_flex.12.grado"), cx=r"grado 12")
        REG("91", Rr("m10b_flex.12.k"), cx=r"91 parámetros")
        REG("3", Rr("m10b_flex.1.k"), cx=r"3 parámetros")
        REG("200", A(lambda: 200 if r("m10b_flex.12.int_max_km2") > 200 else -1, "la intensidad ajustada con grado 12 llega a 208 sedes por km²"), cx=r"más de 200")
        # las sedes repetidas y la cercanía a 100 m
        REG("29.8", Rr("m11b_dups.pct_vecino_menos_100m"))
        REG("16.3", Rr("m11b_dups.pct_vecino_menos_100m_modelo"))
        REG("1.2", Rr("m11b_dups.pct_vecino_menos_100m_modelo_sd"))
        REG("99", Rr("m11b_dups.simulaciones_modelo"), cx=r"99 patrones")
        REG("79", Rr("m11b_dups.sedes_en_esos_sitios"))
        REG("39", Rr("m11b_dups.sitios_con_repetidas"), cx=r"en 39 sitios")
        REG("100", P("distancia de 100 m con que se mide el vecino más próximo (decisión de la medición)"), cx=r"menos de 100 m")
        # κ, μ y el estimador de K
        REG("0.13", [A(lambda: 100 * abs(r("m11_MatClust.iso.parametros.kappa") / r("m11_Thomas.iso.parametros.kappa") - 1), "cambio relativo de κ de Thomas a Matérn con K isotrópica (%)"),
                     A(lambda: 100 * abs(r("m11_MatClust.iso.mu") / r("m11_Thomas.iso.mu") - 1), "cambio relativo de μ de Thomas a Matérn con K isotrópica (%)")])
        REG("0.29", [A(lambda: 100 * abs(r("m11_MatClust.translate.parametros.kappa") / r("m11_Thomas.translate.parametros.kappa") - 1), "cambio relativo de κ de Thomas a Matérn con K de traslación (%)"),
                     A(lambda: 100 * abs(r("m11_MatClust.translate.mu") / r("m11_Thomas.translate.mu") - 1), "cambio relativo de μ de Thomas a Matérn con K de traslación (%)")])
        REG("5.7121", A(lambda: 1e6 * r("m11_Thomas.iso.parametros.kappa") * r("m11_Thomas.iso.mu"), "κ · μ (sedes por km²) de kppm con K isotrópica: el λ̂ del ppm forzado"))
        REG("27.0", A(lambda: r("urbana.n_urbana") / (r("urbana.area_km2") * 1e6) / r("m11_Thomas.iso.parametros.kappa"), "μ con n / |W| en vez del λ̂ forzado: (n / |W|) / κ, K isotrópica"))
        REG("52.2", A(lambda: r("urbana.n_urbana") / (r("urbana.area_km2") * 1e6) / r("m11_Thomas.translate.parametros.kappa"), "μ con n / |W| en vez del λ̂ forzado: (n / |W|) / κ, K de traslación"))
        REG("1975", E("ayuda_b.redwood", "Strauss (1975)"))
        REG("1977", E("ayuda_b.redwood", "Ripley (1977)"))
        # el valle del contraste mínimo
        REG("0.183", A(lambda: r("m11_Thomas.iso.parametros.kappa") * r("m11_Thomas.iso.parametros.scale") ** 2, "κ σ² de Thomas con K isotrópica"))
        REG("0.190", A(lambda: r("m11_Thomas.translate.parametros.kappa") * r("m11_Thomas.translate.parametros.scale") ** 2, "κ σ² de Thomas con K de traslación"))
        REG("5.5", Rr("m11b_kemp.dif_max_pct"))
        REG("1.93", A(lambda: r("m11_Thomas.iso.parametros.kappa") / r("m11_Thomas.translate.parametros.kappa"), "κ isotrópica / κ de traslación (= 1/κ de traslación entre 1/κ isotrópica)"))
        # los errores estándar de kppm y la aproximación rápida de vcov
        REG("26", [A(lambda: round(r("m11b_vcov.efecto_defecto")), "efecto de diseño con la aproximación por defecto, redondeado"),
                   A(lambda: round(r("m11b_vcov.efecto_exacto")), "efecto de diseño con fast = FALSE, redondeado")], cx=r"unas 26")
        REG("80", [A(lambda: round(r("m11b_vcov.n_efectivo_defecto") / 10) * 10, "n efectivo con la aproximación por defecto, a la decena"),
                   A(lambda: round(r("m11b_vcov.n_efectivo_exacto") / 10) * 10, "n efectivo con fast = FALSE, a la decena")], cx=r"unas 80")
        REG("26.1", Rr("m11b_vcov.efecto_exacto"))
        REG("80.6", Rr("m11b_vcov.n_efectivo_exacto"))
        REG("1.59e-07", Rr("m11b_trend.translate.kappa"))
        REG("1067", Rr("m11b_trend.translate.scale"))
        REG("1.09e-07", Rr("m11_Thomas.translate.parametros.kappa"))
        # Hawkes: el índice depende del intervalo y de la realización
        REG("4000", Rr("m11_hawkes.T"))
        REG("200", Rr("m11b_hawkes.por_intervalos[3].k"), cx=r"200 intervalos")
        REG("20", Rr("m11b_hawkes.por_intervalos[3].ancho"), cx=r"20 unidades")
        REG("20", Rr("m11b_hawkes.por_intervalos[0].k"), cx=r"con 20 intervalos")
        REG("2000", Rr("m11b_hawkes.por_intervalos[6].k"), cx=r"con 2000")
        REG("5.15", A(lambda: round(r("m11_hawkes.dispersion_hawkes"), 2), "índice de dispersión del Hawkes, a dos decimales"))
        REG("0.96", A(lambda: round(r("m11_hawkes.dispersion_poisson"), 2), "índice de dispersión del Poisson, a dos decimales"))
        REG("5", A(lambda: round(r("m11_hawkes.veces_mas_agregado")), "veces más agregado (5.38), redondeado"), cx=r"unas 5 veces")
        REG("5.0", A(lambda: round(r("m11b_hawkes.disp_media"), 1), "media del índice de dispersión del Hawkes en 200 réplicas"), cx=r"ronda 5\.0|5\.0 de media")
        REG("0.6", A(lambda: round(r("m11b_hawkes.disp_sd"), 1), "desviación típica del índice de dispersión del Hawkes en 200 réplicas"))
        REG("1.1653", Rr("m11b_hawkes.tasa_media"))
        REG("9.9", Rr("m11b_hawkes.por_intervalos[0].hawkes"), cx=r"9\.9 con 20")
        REG("2.9", Rr("m11b_hawkes.por_intervalos[6].hawkes"), cx=r"2\.9 con 2000")

        # ---- afirmaciones que no son una cifra ----
        AF(2, "En las tres curvas `rhohat` el mínimo cae fuera del bulto; el máximo, solo en la pendiente de `bei`",
           lambda: all(d(f"m7.{k}.rho_min") < d(f"m7.{k}.rho_min_bulto") for k in ("bei.elevacion", "bei.pendiente", "bogota.curva"))
           and d("m7.bei.pendiente.rho_max") > d("m7.bei.pendiente.rho_max_bulto")
           and d("m7.bei.elevacion.rho_max") == d("m7.bei.elevacion.rho_max_bulto")
           and d("m7.bogota.curva.rho_max") == d("m7.bogota.curva.rho_max_bulto"))
        AF(2, "Por el titular (razón en todo el rango) el orden es Bogotá, elevación, pendiente; por el bulto, el inverso",
           lambda: d("m7.bogota.curva.razon") > d("m7.bei.elevacion.razon") > d("m7.bei.pendiente.razon")
           and d("m7.bei.pendiente.razon_bulto") > d("m7.bei.elevacion.razon_bulto") > d("m7.bogota.curva.razon_bulto"))
        AF(2, "`ppm(pu ~ 1)` es exacto y, con `forcefit = TRUE`, ajusta con `glm`",
           lambda: r("m8_homogeneo.fitter") == "exact" and r("m8_homogeneo.forzado.fitter") == "glm")
        AF(2, "Con `nd = 300` el modelo constante sigue siendo exacto y con el mismo AIC",
           lambda: r("m8_constante_nd300.fitter") == "exact" and r("m8_constante_nd300.mismo") is True)

        def aics():
            return [r(f"m8_nd.filas[{i}].aic") for i in range(4)]

        def sinc():
            return [r(f"m8_nd.filas[{i}].sin_contar_km2") for i in range(4)]

        AF(2, "El AIC baja de nd = 50 a 100, queda casi quieto de 100 a 200 y sube a 300",
           lambda: aics()[0] > aics()[1] and abs(aics()[1] - aics()[2]) < 0.05 and aics()[3] > aics()[2])
        AF(2, "El AIC sigue a la ciudad sin contar en sentido inverso: a más área sin contar, menos AIC",
           lambda: all(aics()[i] > aics()[j] for i in range(4) for j in range(4) if sinc()[i] < sinc()[j] - 1e-9))
        AF(2, "Con la integral bien hecha el constante gana a `dcen` por 0.07 y, por la misma cuadratura, por 0.51644; con los AIC de `ppm`, `dcen` gana por 13.44572",
           lambda: r("m8_nd.gana_distancia_ppm") > 13 and 0 < r("m8_nd.gana_constante_exacta") < 0.1 and 0 < r("m8_nd.gana_constante_misma") < 1)
        AF(2, "La ventaja de `dcen` con los AIC de `ppm` es el AIC del constante exacto menos el de `dcen` por defecto",
           lambda: abs((r("m8_homogeneo.aic") - r("m8_nd.filas[1].aic")) - r("m8_nd.gana_distancia_ppm")) < 1e-6)
        AF(2, "El ajuste crudo no da errores estándar: `vcov()` es NULL, `sqrt(diag(NULL))` mide 0 × 0 y no hay un error estándar por coeficiente",
           lambda: r("m9.crudo.vcov_es_null") is True and r("m9.crudo.dim_sqrt_diag_null") == [0, 0] and r("m9.crudo.length_ee_igual_a_coef") is False)
        AF(2, "El ajuste crudo y el centrado tienen el mismo AIC (es el mismo modelo)",
           lambda: abs(r("m9.crudo.aic") - r("m9.centrado.aic")) < 1e-6)
        AF(2, "Centrar y pasar a kilómetros mejora el condicionamiento",
           lambda: r("m9.centrado.cond") > r("m9.crudo.cond") and r("m9.mejora_condicion") > 1e8)
        AF(2, "Con errores estándar de Poisson, `xc` pasa de 1.96 en valor absoluto; `yc` y `dcen`, no",
           lambda: abs(r("m9.centrado.z[1]")) > 1.96 > max(abs(r("m9.centrado.z[2]")), abs(r("m9.distancia.z[1]"))))

        def banda():
            c = d("m10.curva")
            idx = [i for i, x in enumerate(c["r"]) if x > 0]
            arriba = [i for i in idx if c["obs"][i] > c["hi"][i]]
            abajo = [i for i in idx if c["obs"][i] < c["lo"][i]]
            return c, idx, arriba, abajo

        AF(2, "Los 62 radios fuera de la banda (de 100) están todos por encima; ninguno por debajo",
           lambda: (lambda c, idx, a, b: len(idx) == 100 and len(a) == 62 and len(b) == 0)(*banda()))
        AF(2, "El tramo fuera de la banda es contiguo, va de 58.68 a 3638.23 m y los 38 nodos que siguen están dentro",
           lambda: (lambda c, idx, a, b: abs(c["r"][a[0]] - 58.68) < 0.01 and abs(c["r"][a[-1]] - 3638.23) < 0.01
                    and a == list(range(a[0], a[-1] + 1)) and len([i for i in idx if i > a[-1]]) == 38)(*banda()))
        AF(2, "La peor desviación del patrón (MAD) cae dentro del tramo; las 3 simulaciones que la superan están pasado su final",
           lambda: d("m10.test_global.mad_superan") == 3 and d("m10.primer_r_fuera_m") < d("m10.test_global.r_mad_observada_m") < d("m10.ultimo_r_fuera_m")
           and d("m10.test_global.r_min_mad_superan_m") > d("m10.ultimo_r_fuera_m"))
        AF(2, "Con 39 simulaciones el p mínimo posible es 1/(39 + 1) y DCLF y MAD lo alcanzan; con 999, el DCLF alcanza 1/(999 + 1)",
           lambda: abs(r("m10_e39.dclf") - 1 / 40) < 1e-12 and abs(r("m10_e39.mad") - 1 / 40) < 1e-12 and abs(r("m10.dclf_p") - 1 / 1000) < 1e-12)
        AF(2, "Leída entera, la banda se cruza más veces que su nivel puntual (7.7 % contra 0.2 %, 38.53854 veces)",
           lambda: r("m10.nativa.pct") > r("m10.nivel_puntual_pct") and abs(r("m10.veces_el_nivel") - r("m10.nativa.pct") / r("m10.nivel_puntual_pct")) < 1e-6)
        AF(2, "La media de las 999 simulaciones queda a menos de 0.65 % de π r² y no a menos de 0.64 %",
           lambda: 0.64 < r("m10.mmean_vs_teorica_pct") < 0.65)

        def tt(c):
            return [r(f"m11_{mm}.{c}.segundos") for mm in MODELOS]

        AF(2, "Los tres tiempos con K isotrópica son del mismo orden (cociente máximo / mínimo menor que 1.05) y los de traslación son más de 100 veces menores",
           lambda: max(tt("iso")) / min(tt("iso")) < 1.05 and all(a / b > 100 for a, b in zip(tt("iso"), tt("translate"))))
        AF(2, "Con K de traslación, en Thomas κ baja y la escala y μ suben",
           lambda: (lambda a, b: b["parametros"]["kappa"] < a["parametros"]["kappa"] and b["parametros"]["scale"] > a["parametros"]["scale"] and b["mu"] > a["mu"])(r("m11_Thomas.iso"), r("m11_Thomas.translate")))
        AF(2, "La escala de Matérn es casi el doble de la de Thomas con cualquiera de las dos correcciones (cociente entre 1.8 y 2.0): son parámetros distintos y no se comparan",
           lambda: all(1.8 < r(f"m11_MatClust.{c}.parametros.scale") / r(f"m11_Thomas.{c}.parametros.scale") < 2.0 for c in ("iso", "translate")))
        AF(2, "`kppm` es determinista: dos corridas con semillas distintas dan el mismo ajuste",
           lambda: r("m11_kppm_determinista.mismo") is True)

        def cambio_max():
            mx = 0.0
            for mm in MODELOS:
                a, b = r(f"m11_{mm}.translate.parametros"), r(f"m11_{mm}.sin_duplicados.parametros")
                for k in a:
                    mx = max(mx, 100 * abs(b[k] - a[k]) / abs(a[k]))
            return mx

        AF(2, "Sin los 40 duplicados, la escala de Thomas pasa de 1320 a 1373 m (4.0 %) y el mayor cambio de todos los parámetros de los tres modelos es 6.2 %",
           lambda: abs(cambio_max() - d("m11.duplicados.cambio_maximo_pct")) < 0.01
           and abs(100 * (r("m11_Thomas.sin_duplicados.parametros.scale") / r("m11_Thomas.translate.parametros.scale") - 1) - 4.03) < 0.01)
        AF(2, "Con conglomerados, los seis errores estándar superan el de Poisson y ninguna |z| llega a 1.96; con K isotrópica el error crece menos que con la de traslación",
           lambda: all(tend(mm, c, "ee") > r("m11_Thomas.tendencia.poisson.ee[1]") and abs(tend(mm, c, "z")) < 1.96 for mm in MODELOS for c in ("iso", "translate"))
           and all(tend(mm, "iso", "inflacion") < tend(mm, "translate", "inflacion") for mm in MODELOS))
        AF(2, "Hawkes: la dispersión supera 1, la del Poisson de su misma tasa queda por debajo de 1 y la tasa simulada queda a menos de 3 % de la teórica",
           lambda: r("m11_hawkes.dispersion_hawkes") > 1 > r("m11_hawkes.dispersion_poisson")
           and abs(r("m11_hawkes.tasa_simulada") / r("m11_hawkes.tasa_teorica") - 1) < 0.03)


        # ---- afirmaciones de la revisión tras la auditoría B ----
        AF(2, "Con la misma envolvente, el plano (grado 1) es rechazado por los dos tests globales y una tendencia de grado 12 (91 parámetros) no lo es, aunque el DCLF queda al borde con el grado 10",
           lambda: all(v["dclf_p"] <= 0.01 and v["mad_p"] <= 0.01 for v in r("m10b_flex.1.semillas").values())
           and all(v["dclf_p"] > 0.05 and v["mad_p"] > 0.05 for v in r("m10b_flex.12.semillas").values())
           and all(0.05 < v["dclf_p"] < 0.06 and v["mad_p"] > 0.2 for v in r("m10b_flex.10.semillas").values()))
        AF(2, "La tendencia de grado 12 llega a más de 200 sedes por km² y a casi cero en otros sitios (imita los grupos), y su AIC con la integral fina es unos 490 puntos menor que el del plano",
           lambda: r("m10b_flex.12.int_max_km2") > 200 and r("m10b_flex.12.int_min_km2") < 0.01
           and 450 < r("m10b_flex.1.aic_integral_fina") - r("m10b_flex.12.aic_integral_fina") < 520)
        AF(2, "El 29.8 % de las sedes tiene otra a menos de 100 m, casi el doble que bajo el modelo con tendencia (16.3 %, sd 1.2); hay 79 sedes en 39 sitios con más de una sede y 40 sedes sobrantes",
           lambda: r("m11b_dups.pct_vecino_menos_100m") > 1.7 * r("m11b_dups.pct_vecino_menos_100m_modelo") and r("m11b_dups.sitios_con_repetidas") == 39
           and r("m11b_dups.sedes_en_esos_sitios") == 79 and r("m11b_dups.sedes_sobrantes") == 40 and r("m11b_dups.sitios_de_2") == 38 and r("m11b_dups.sitios_de_3") == 1)
        AF(2, "Cambiar de familia (Thomas a Matérn) mueve κ y μ menos de 0.3 %; cambiar de estimador (isotrópica a traslación), 48.2 % y 93.2 %",
           lambda: all(100 * abs(r(f"m11_MatClust.{c}.parametros.kappa") / r(f"m11_Thomas.{c}.parametros.kappa") - 1) < 0.3 for c in ("iso", "translate"))
           and all(100 * abs(r(f"m11_MatClust.{c}.mu") / r(f"m11_Thomas.{c}.mu") - 1) < 0.3 for c in ("iso", "translate"))
           and abs(100 * (1 - r("m11_Thomas.translate.parametros.kappa") / r("m11_Thomas.iso.parametros.kappa")) - 48.2) < 0.05
           and abs(100 * (r("m11_Thomas.translate.mu") / r("m11_Thomas.iso.mu") - 1) - 93.2) < 0.05)
        AF(2, "κ · μ de `kppm` es el λ̂ del `ppm` forzado por la cuadratura (5.71211), no n / |W| (5.69321)",
           lambda: abs(1e6 * r("m11_Thomas.iso.parametros.kappa") * r("m11_Thomas.iso.mu") / r("m8_homogeneo.forzado.lambda_km2") - 1) < 1e-6
           and abs(1e6 * r("m11_Thomas.translate.parametros.kappa") * r("m11_Thomas.translate.mu") / r("m8_homogeneo.forzado.lambda_km2") - 1) < 1e-6)
        AF(2, "κσ² es casi igual en los dos ajustes de Thomas (diferencia menor que 5 %) y 1/κ cambia casi el doble; la K isotrópica queda por debajo de la de traslación en todo r > 250 m, hasta 5.5 %",
           lambda: abs(r("m11_Thomas.translate.parametros.kappa") * r("m11_Thomas.translate.parametros.scale") ** 2
                       / (r("m11_Thomas.iso.parametros.kappa") * r("m11_Thomas.iso.parametros.scale") ** 2) - 1) < 0.05
           and 1.9 < r("m11_Thomas.iso.parametros.kappa") / r("m11_Thomas.translate.parametros.kappa") < 2.0
           and r("m11b_kemp.dif_min_pct") > 0 and 5.4 < r("m11b_kemp.dif_max_pct") < 5.6)
        AF(2, "La g inhomogénea sale de su banda sin interrupción hasta 2.2 km (89 radios seguidos) y vale 1.20 a 1 km y 1.06 a 2 km, mientras la K sigue fuera de la banda hasta 3.6 km (5028) o más",
           lambda: r("m10b_pcf.primera_racha_largo") == 89 and 2.2 <= r("m10b_pcf.primera_racha_hasta_r") / 1000 < 2.3
           and r("m10.ultimo_r_fuera_m") > r("m10b_pcf.primera_racha_hasta_r"))
        AF(2, "`rhohat` con `jitter = FALSE` da lo mismo en cada corrida y no consume el generador; con `jitter = TRUE` difiere y sí lo consume",
           lambda: r("m7b_jitter.identico_con_FALSE") is True and r("m7b_jitter.distinto_con_TRUE") is True
           and r("m7b_jitter.consume_rng_con_FALSE") is False and r("m7b_jitter.consume_rng_con_TRUE") is True)
        AF(2, "El ancho del núcleo mueve el titular de Bogotá (de 3 063 con la mitad del ancho a 2.39 con cuatro veces) y el bulto (de 2.10 a 1.11), pero la cola infla la razón a cualquier ancho",
           lambda: r("m7b_adjust.total[0]") > 3000 and r("m7b_adjust.total[3]") < 2.4 and r("m7b_adjust.bulto[0]") > r("m7b_adjust.bulto[3]")
           and all(t > b for t, b in zip(r("m7b_adjust.total"), r("m7b_adjust.bulto"))))
        AF(2, "El condicionamiento de la matriz de diseño cruda (1.794e-10) es mayor que la tolerancia de `solve` (2.2e-16) y el de la información de Fisher (2.7e-20) es menor; `solve` falla con ella",
           lambda: r("m9b_info.sv_diseno_crudo") > r("m9b_info.tolerancia_solve") > r("m9b_info.rcond_info_crudo") and r("m9b_info.solve_falla") is True)
        AF(2, "Con `fast = FALSE` el efecto de diseño de Thomas con K de traslación (26.1) y las 2 107 sedes (80.6 efectivas) casi no cambian respecto de la aproximación por defecto (26.03409 y 80.93235)",
           lambda: abs(r("m11b_vcov.efecto_defecto") - d("m11.tendencia.efecto_diseno")) < 1e-6 and abs(r("m11b_vcov.efecto_exacto") / r("m11b_vcov.efecto_defecto") - 1) < 0.01
           and r("m11b_vcov.fast_por_defecto") is True)
        AF(2, "Los `kppm` con tendencia (`~ xc + yc`) tienen otros parámetros de grupo que los de `~ 1`: Thomas con K de traslación, κ = 1.59e-07 y σ = 1067 m contra 1.09e-07 y 1320 m",
           lambda: abs(r("m11b_trend.translate.kappa") / r("m11_Thomas.translate.parametros.kappa") - 1) > 0.3
           and abs(r("m11b_trend.translate.scale") / r("m11_Thomas.translate.parametros.scale") - 1) > 0.15)
        AF(2, "El índice de dispersión del Hawkes cambia con el tamaño del intervalo (de 9.9 con 20 intervalos a 2.9 con 2000) y entre realizaciones (media 5.0, sd 0.6 en 200 réplicas); la tasa simulada está a media desviación de una réplica de la teórica",
           lambda: r("m11b_hawkes.por_intervalos[0].hawkes") > 9 and r("m11b_hawkes.por_intervalos[6].hawkes") < 3
           and abs(r("m11b_hawkes.z_tasa_simulada")) < 1 and r("m11b_hawkes.replicas") == 200)

        AF(2, "Evaluado cada contraste mínimo de Thomas en los parámetros del otro ajuste sube casi el triple (178 % y 195 % sobre su mínimo) y, con κ reoptimizado, el de traslación ya sube más de la mitad en σ = 932 m: no es un valle casi plano; el objetivo propio coincide con el de spatstat (×513)",
           lambda: 2.5 < 1 + r("m11b_valle.cruzada_traslacion_en_par_iso_pct") / 100 < 3.1 and 2.5 < 1 + r("m11b_valle.cruzada_isotropica_en_par_trasl_pct") / 100 < 3.1
           and r("m11b_valle.perfil_traslacion_sigma_isotropico_pct") > 50 and abs(r("m11b_valle.objetivo_propio_sobre_spatstat") - 513) < 1e-6)
        AF(2, "`kppm` ajusta por contraste mínimo por defecto (no evalúa una verosimilitud) y `vcov(kppm)` con esta cuadratura da lo mismo que `fast = TRUE`, que la ayuda dice que subestima las varianzas",
           lambda: "(the default) clustering" in r("ayuda_b.kppm").replace("\n", " ") and "underestimate" in r("ayuda_b.vcov_kppm")
           and r("m11b_vcov.defecto_igual_fast_TRUE") is True and r("m11b_vcov.efecto_defecto") < r("m11b_vcov.efecto_exacto"))
        AF(2, "Los óptimos propios del contraste (κ y σ de Thomas con cada K) coinciden con los de `kppm` con tres cifras",
           lambda: abs(r("m11b_valle.traslacion.kappa") / r("m11_Thomas.translate.parametros.kappa") - 1) < 1e-3
           and abs(r("m11b_valle.traslacion.sigma") / r("m11_Thomas.translate.parametros.scale") - 1) < 1e-3
           and abs(r("m11b_valle.isotropica.kappa") / r("m11_Thomas.iso.parametros.kappa") - 1) < 1e-3
           and abs(r("m11b_valle.isotropica.sigma") / r("m11_Thomas.iso.parametros.scale") - 1) < 1e-3)

        # ---- tablas: cada celda numérica en su casilla ----
        def fila_nd(i, nd):
            f = lambda k: (lambda: r(f"m8_nd.filas[{i}].{k}"))
            return [[nd], [f("ficticios")], [f("sin_contar_km2")], [f("aic")], [f("logver_ppm")], [f("logver_exacta")]]
        TAB(2, "Un modelo, cuatro cuadraturas", [fila_nd(i, nd) for i, nd in enumerate((50, 100, 200, 300))])
        TAB(2, "Habría evidencia del gradiente", [
            [None, None, [lambda: r("m9.centrado.coef[1]")], [lambda: r("m9.centrado.ee[1]")], [lambda: r("m9.centrado.z[1]")]],
            [None, None, [lambda: r("m9.centrado.coef[2]")], [lambda: r("m9.centrado.ee[2]")], [lambda: r("m9.centrado.z[2]")]],
            [None, None, [lambda: r("m9.distancia.coef[1]")], [lambda: r("m9.distancia.ee[1]")], [lambda: r("m9.distancia.z[1]")]]])
        escala = lambda mm, c: (lambda: r(f"m11_{mm}.{c}.parametros.scale"))
        seg = lambda i: (lambda: d(f"m11.ajustes[{i}].segundos"))
        TAB(2, "Tres familias de conglomerado", [
            [None, None, [escala("Thomas", "iso"), escala("Thomas", "translate")], [seg(0), seg(1)]],
            [None, None, [escala("MatClust", "iso"), escala("MatClust", "translate")], [seg(2), seg(3)]],
            [None, None, [escala("LGCP", "iso"), escala("LGCP", "translate")], [seg(4), seg(5)]]])

        def fila_z(mm, c):
            return [None, [lambda: tend(mm, c, "ee")], [lambda: tend(mm, c, "z")], [lambda: tend(mm, c, "inflacion")]]
        TAB(2, "Con conglomerados, el error estándar", [
            [None, [lambda: r("m11_Thomas.tendencia.poisson.ee[1]")], [lambda: r("m9.centrado.z[1]")], None],
            fila_z("Thomas", "iso"), fila_z("Thomas", "translate"),
            fila_z("MatClust", "iso"), fila_z("MatClust", "translate"),
            fila_z("LGCP", "iso"), fila_z("LGCP", "translate")])
        TAB(2, "El proyecto integrador declara", [
            [None, None, [lambda: r("urbana.n_capa"), lambda: r("urbana.n_urbana")]],
            [None, None, [lambda: r("anchos.caida_pct"), lambda: r("anchos.sigmas_m[0]"), lambda: r("anchos.sigmas_m[6]")]],
            [None, None, [800, lambda: r("bordes.800.masa_defecto"), lambda: r("bordes.800.masa_diggle")]],
            [None, None, [lambda: r("m8_nd.rango_aic")]],
            [None, None, [lambda: r("m11_Thomas.iso.mu"), lambda: r("m11_Thomas.translate.mu")]]])
