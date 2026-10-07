#!/usr/bin/env python3
"""
prueba_auditor_preparcial2.py — le rompe el preparcial del Corte II al auditor (P1.3)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Preparcial_Corte_2.md.

`audita_preparcial2.py` informó 131 comprobaciones y 0 fallos el día que nació,
y ese número no dice nada hasta haberlo visto fallar. Este arnés es el de
`prueba_auditor_preparcial1.py` con una superficie más:

  · el JSON del preparcial (cifras nuevas, ejercicios, gráficos, catálogo);
  · el HTML publicado (las preguntas solo viven ahí);
  · los JSON de los capítulos 4 y 5, porque la desincronización que existe
    de verdad no la provoca el preparcial: la provoca un capítulo que se
    regenera debajo;
  · y los CSV de Murchison, la fuente primaria de los ejercicios.

Las tres reglas de siempre: CONTROL limpio al entrar y al salir; ninguna
inyección inerte (si no cambia el archivo, es culpa del arnés y se dice);
y un auditor que REVIENTA no ha cazado nada. Y se cuentan los TIPOS de
comprobación que se han visto fallar, no solo los defectos cazados.

Uso:  python3 precalculo/prueba_auditor_preparcial2.py
Tarda unos minutos: cada inyección es una corrida entera del auditor.
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

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_preparcial2.py"
sys.path.insert(0, str(PRECALCULO))
from prueba_auditor_base import avisa_rotulos_largos  # noqa: E402

DATOS = SALIDAS / "preparcial2_datos.json"
HTML = RAIZ / "Htmls_Espacial" / "preparcial-corte-2.html"
CAPS = ["cap4_datos.json", "cap5_datos.json"]
MURCH = ["preparcial2_murchison_oro.csv", "preparcial2_murchison_fallas.csv",
         "preparcial2_murchison_greenstone.csv", "preparcial2_murchison_ventana.csv"]
PY = json.loads((PRECALCULO / "versiones_py.json").read_text(encoding="utf-8"))["ejecutable"]


# =====================================================================
# Las mutaciones
# =====================================================================
def poner(ruta, valor):
    """Cambia `ruta` (claves separadas por punto, índices en base 0) en un
    objeto JSON."""
    def f(o):
        partes = ruta.split(".")
        cur = o
        for p in partes[:-1]:
            cur = cur[int(p)] if isinstance(cur, list) else cur[p]
        ult = partes[-1]
        if isinstance(cur, list):
            ult = int(ult)
        cur[ult] = valor(cur[ult]) if callable(valor) else valor
    return f


def varios(*fs):
    def f(o):
        for g in fs:
            g(o)
    return f


def correctas_delante(t: str) -> str:
    """Reordena las opciones de cada pregunta para que la correcta vaya
    delante: lo que el preparcial del Corte I publicó sin querer."""
    def una(m):
        bloque = m.group(0)
        ops = re.findall(r"          \{ texto: .*?\n            retro: .*? \}(?=,\n|\n        \])", bloque, re.S)
        if len(ops) < 2:
            return bloque
        orden = sorted(ops, key=lambda o: "correcta: true" not in o)
        return "        opciones: [\n" + ",\n".join(orden) + "\n        ]"
    return re.sub(r"        opciones: \[\n.*?\n        \]", una, t, flags=re.S)


def correctas_largas(t: str) -> str:
    """Alarga 40 caracteres el texto de cada opción correcta."""
    return re.sub(r'(\{ texto: "(?:[^"\\]|\\.)*?)(", correcta: true)',
                  r"\1, y esto lo dice la clave muy por extenso\2", t)


def quita_pregunta(t: str) -> str:
    """Quita la primera pregunta del bloque A (la única del módulo 4.1)."""
    i = t.index("AUTOEVALUACIONES['bloque-a'] = [")
    j = t.index("\n      {", i)
    k = t.index("\n      },\n", j) + len("\n      },")
    return t[:j] + t[k:]


def quita_ejercicio(t: str) -> str:
    i = t.index('<div class="ejercicio-guiado">')
    j = t.index('<div class="ejercicio-guiado">', i + 10)
    return t[:i] + t[j:]


def defectos():
    D = []
    def obj(nombre, f, destino="datos"):
        D.append((nombre, destino, "obj", f))
    def txt(nombre, busca, pone):
        D.append((nombre, "html", "txt", (busca, pone)))
    def fun(nombre, f, destino="html"):
        D.append((nombre, destino, "fun", f))

    # ---- familia 1 · cifras nuevas (JSON) ----------------------------
    obj("A3 · R urbana cambiada", poner("nuevo.ce_ventana.ce_urb", lambda v: v * 1.01))
    obj("A3 · sedes urbanas cambiadas", poner("nuevo.ce_ventana.n_urb", 2108))
    obj("A5 · χ² 5×5 del original cambiado", poner("nuevo.rebarajado.chi2_5_orig", lambda v: v + 1))
    obj("A5 · χ² 10×10 del original cambiado", poner("nuevo.rebarajado.chi2_10_orig", lambda v: v + 1))
    obj("A3 · R del D.C. cambiada", poner("nuevo.ce_ventana.ce_dc", lambda v: v * 1.01))
    obj("A3 · sedes del D.C. cambiadas", poner("nuevo.ce_ventana.n_dc", 2209))
    obj("A3 · R del D.C. por encima de la urbana", poner("nuevo.ce_ventana.ce_dc", 0.9))
    obj("A5 · χ² 10×10 del rebarajado cambiado", poner("nuevo.rebarajado.chi2_10_reb", lambda v: v + 1))
    obj("A5 · χ² 5×5 del rebarajado cambiado", poner("nuevo.rebarajado.chi2_5_reb", lambda v: v + 1))
    obj("A11 · nrank sin el 2", poner("nuevo.nrank.correcto", 10))
    obj("A11 · nivel por defecto mal", poner("nuevo.nrank.nivel_defecto_pct", 0.5))
    obj("A11 · p mínimo mal", poner("nuevo.nrank.p_minimo", 0.01))
    obj("B3 · tope en la mitad del lado", poner("nuevo.tope_ppl.correcto", 2000))
    obj("B3 · casi nadie choca", poner("nuevo.tope_ppl.csr_chocan_en_el_tope", 2))
    obj("B6 · riesgo relativo contra la global", poner("nuevo.riesgo_relativo.correcto", 6.05))
    obj("B8 · Kennedy con una sede de más", poner("nuevo.forzado.n", 263))
    obj("B8 · área de Kennedy mal", poner("nuevo.forzado.area_km2", lambda v: v * 1.01))
    obj("B8 · la fórmula cerrada mal", poner("nuevo.forzado.distractores.0.valor", lambda v: v * 1.01))
    obj("B8 · λ forzada que no cuadra con Σw", poner("nuevo.forzado.correcto", lambda v: v * 1.01))
    obj("B8 · la cuadratura ve más área", varios(poner("nuevo.forzado.suma_pesos_km2", 39.0),
                                                 poner("nuevo.forzado.correcto", lambda v: 262 / 39.0)))
    obj("B8 · área sin contar mal", poner("nuevo.forzado.sin_contar_km2", lambda v: v * 2))
    obj("B1 · la KDE con σ enorme no es plana", poner("nuevo.limite.corregida_max_km2", 7.5))
    obj("A7 · mediana de CSR mal", poner("nuevo.gf_suecos.csr_mediana_m", lambda v: v * 1.1))
    obj("A7 · G llega pronto", poner("nuevo.gf_suecos.g_mediana_m", 0.4))
    obj("A7 · J bajo 1 en algún nodo", poner("nuevo.gf_suecos.j_sobre_1", 30))
    obj("B9 · exp(β) mal", poner("nuevo.ebeta.factor_por_km", lambda v: v * 1.01))
    obj("B9 · porcentaje por km mal", poner("nuevo.ebeta.pct_por_km", lambda v: v * 2))
    obj("B10 · σ de Kinhom mal", poner("nuevo.kinhom_nucleo.sigma_nucleo_m", lambda v: v * 1.1))
    obj("B3 · los que chocan y los que no, mal", poner("nuevo.tope_ppl.csr_no_chocan", 8))
    obj("B3 · un ancho finito sobre el tope", poner("nuevo.tope_ppl.csr_sigma_max_m", 3000))
    obj("B3 · puntos esperados mal", poner("nuevo.tope_ppl.csr_puntos_esperados", 200))
    obj("C3 · nivel del cap. 4 mal", poner("nuevo.niveles.cap4_pct", 2.5))
    obj("C5 · n efectivo sin el cuadrado", poner("nuevo.n_efectivo.correcto", 530.7))
    obj("A1 · una sede de más en el resto", poner("nuevo.resto_dc.n_resto", 102))
    obj("A1 · área del resto mal", poner("nuevo.resto_dc.area_resto_km2", lambda v: v * 1.01))
    obj("A1 · cociente contra el D.C. entero", poner("nuevo.resto_dc.correcto", 4.21))
    obj("A4 · la media de R no baja", poner("nuevo.denso.R_media", 1.058))
    obj("A4 · casi ninguna bajo 1", poner("nuevo.denso.pct_bajo1", 5))
    obj("A10 · el solape hacia el este mal", poner("nuevo.traslacion.frac_este_100", lambda v: v - 1))
    obj("A10 · el peso no es el inverso", poner("nuevo.traslacion.peso_este_100", 1))
    obj("A10 · el peso baja con la distancia", poner("nuevo.traslacion.peso_este_1000", 1.01))
    obj("A10 · el solape hacia el norte mal", poner("nuevo.traslacion.frac_norte_100", lambda v: v - 1))
    obj("A10 · el solape a 1 km mal", poner("nuevo.traslacion.frac_este_1000", lambda v: v + 1))
    obj("A10 · la norte-sur pesa más", poner("nuevo.traslacion.peso_norte_100", lambda v: v + 0.01))
    obj("A4 · el sesgo desaparece", poner("nuevo.denso.R_media", 0.99))
    obj("B11 · distancia media de Matérn mal", poner("nuevo.escalas.matern_media_m", lambda v: v * 1.1))
    obj("B11 · distancia media de Thomas mal", poner("nuevo.escalas.thomas_media_m", lambda v: v * 1.1))
    obj("B11 · las escalas ya casi iguales", poner("nuevo.escalas.razon_escalas", 1.1))
    obj("C3 · cobertura de la banda mal", poner("nuevo.niveles.cap4_cobertura_pct", 99))
    obj("C2 · diferencia isotrópica/traslación mal", poner("nuevo.iso_tras.max_dif_pct", lambda v: v * 1.1))
    obj("C2 · radio de la diferencia mal", poner("nuevo.iso_tras.r_max_dif_m", lambda v: v + 58.68))
    obj("catálogo · rechazos sin supuesto mal", poner("nuevo.supuesto_rw.rechazos_sin_supuesto", 9))
    obj("E1 · un yacimiento menos", poner("ejercicios.e1.solucion.n", 254))
    obj("E1 · uno más en el greenstone", poner("ejercicios.e1.solucion.n_gs", 220))
    obj("E1 · área del greenstone mal", poner("ejercicios.e1.solucion.area_gs", lambda v: v * 1.01))
    obj("E1 · área del rectángulo mal", poner("ejercicios.e1.solucion.area_rect", lambda v: v * 1.01))
    obj("E1 · cociente mal", poner("ejercicios.e1.solucion.cociente", lambda v: v * 1.1))
    obj("E1 · χ² de la rejilla 5×5 mal", poner("ejercicios.e1.solucion.cuadrantes.3.chi2", lambda v: v + 1))
    obj("E1 · esperanza de la rejilla 5×5 mal",
        poner("ejercicios.e1.solucion.cuadrantes.3.esperanza_min", lambda v: v * 1.1))
    obj("E1 · p de la rejilla 5×5 mal", poner("ejercicios.e1.solucion.cuadrantes.3.p", lambda v: v * 10))
    obj("E1 · rejillas que respetan, una menos", poner("ejercicios.e1.solucion.respetan", [2, 3, 4, 5, 6]))
    obj("E1 · la resta no pierde ninguno", poner("ejercicios.e1.solucion.n_fuera_resta", 36))
    obj("E1 · cociente de la resta mal", poner("ejercicios.e1.solucion.cociente_resta", lambda v: v * 1.05))
    obj("E1 · el Poisson del greenstone no rechaza",
        poner("ejercicios.e1.solucion.rechazos_greenstone.0", 90))
    obj("E1 · la mediana simulada sobre el oro",
        poner("ejercicios.e1.solucion.chi2_mediana_greenstone.0", 1e6))
    obj("E2 · un vecino fuera de más", poner("ejercicios.e2.solucion.vecino_fuera", 12))
    obj("E2 · vecino medio dentro mal", poner("ejercicios.e2.solucion.nn_media_gs_km", lambda v: v * 1.01))
    obj("E2 · vecino medio del rectángulo mal", poner("ejercicios.e2.solucion.nn_media_rect_km", lambda v: v * 1.01))
    obj("E2 · vecino del azar en el greenstone mal",
        poner("ejercicios.e2.solucion.nn_esperada_gs_km", lambda v: v * 1.01))
    obj("E2 · vecino del azar en el rectángulo mal",
        poner("ejercicios.e2.solucion.nn_esperada_rect_km", lambda v: v * 1.01))
    obj("E2 · K/πr² a 2 km mal", poner("ejercicios.e2.solucion.K_none_sobre_pir2_2km", lambda v: v * 1.01))
    obj("E2 · el cruce más lejos", poner("ejercicios.e2.solucion.r_cruce_km", 9.5))
    obj("E2 · núcleo del greenstone mal", poner("ejercicios.e2.solucion.pct_area_a_mas_de_10km", lambda v: v * 2))
    obj("E2 · el azar del greenstone ya agrupa más",
        poner("ejercicios.e2.solucion.ref_K_cuantiles.2", 400))
    obj("E2 · R ingenua del greenstone mal", poner("ejercicios.e2.solucion.ce_naive", lambda v: v * 1.01))
    obj("E2 · R ingenua del rectángulo mal", poner("ejercicios.e2.solucion.ce_rect", lambda v: v * 1.01))
    obj("E2 · piezas contadas con los agujeros", poner("ejercicios.e2.solucion.piezas", 133))
    obj("E2 · un agujero menos", poner("ejercicios.e2.solucion.agujeros", 17))
    obj("E2 · vértices mal", poner("ejercicios.e2.solucion.vertices", 7000))
    obj("E2 · perímetro mal", poner("ejercicios.e2.solucion.perimetro_km", lambda v: v * 1.01))
    obj("E2 · K sin corregir mal", poner("ejercicios.e2.solucion.K_none", lambda v: v * 1.01))
    obj("E2 · K de traslación lejos de la exacta", poner("ejercicios.e2.solucion.K_trans", lambda v: v * 1.1))
    obj("E2 · πr² por encima de la corregida", poner("ejercicios.e2.solucion.pir2", 600))
    obj("E2 · fracción cerca del borde mal", poner("ejercicios.e2.solucion.pct_borde_gs", lambda v: v - 5))
    obj("E2 · la de Bogotá mal", poner("ejercicios.e2.solucion.pct_borde_bogota", lambda v: v * 2))
    obj("E2 · mediana al borde mal", poner("ejercicios.e2.solucion.mediana_borde_km", lambda v: v * 1.1))
    obj("E2 · la corregida del rectángulo por encima", poner("ejercicios.e2.solucion.ce_rect_cdf", 0.4))
    obj("E3 · cociente de selectores mal", poner("ejercicios.e3.solucion.razon", lambda v: v * 1.1))
    obj("E3 · un selector chocó", poner("ejercicios.e3.solucion.selectores.0.choco", True))
    obj("E3 · masa sin corregir mal", poner("ejercicios.e3.solucion.masas_cvl.sin", lambda v: v * 1.05))
    obj("E3 · masa sin corregir del σ estrecho mal",
        poner("ejercicios.e3.solucion.masas_diggle.sin", lambda v: v * 0.99))
    obj("E3 · Diggle no integra n", poner("ejercicios.e3.solucion.masas_cvl.dig", 254.5))
    obj("E3 · la por defecto se queda corta con los dos", poner("ejercicios.e3.solucion.masas_cvl.def", 250))
    obj("E3 · el pico de bw.CvL por encima del greenstone", poner("ejercicios.e3.solucion.picos.CvL", 0.03))
    obj("E3 · la intensidad del greenstone no es la del E1",
        poner("ejercicios.e3.solucion.lambda_gs", lambda v: v * 1.1))
    obj("E3 · la rejilla fina ya no basta", poner("ejercicios.e3.solucion.celda_fina_km.1", 1.0))
    obj("E4 · percentil 5 mal", poner("ejercicios.e4.solucion.bulto.0", lambda v: v * 1.1))
    obj("E4 · percentil 95 mal", poner("ejercicios.e4.solucion.bulto.1", lambda v: v * 1.1))
    obj("E4 · yacimiento más alejado mal", poner("ejercicios.e4.solucion.dist_max_oro", lambda v: v + 1))
    obj("E4 · AIC sin el 2", poner("ejercicios.e4.solucion.dif_aic", lambda v: v / 2))
    obj("E4 · cociente exacto mal", poner("ejercicios.e4.solucion.cociente_exacto", lambda v: v * 1.1))
    obj("E4 · nd = 400 se pasa del exacto", poner("ejercicios.e4.solucion.eb_400", 70))
    obj("E4 · nd = 400 acierta peor el área", poner("ejercicios.e4.solucion.pesos_gs_400", 20000))
    obj("E4 · ρ mínimo no es cero", poner("ejercicios.e4.solucion.rho_min", 1e-5))
    obj("E4 · los ceros de ρ antes del último yacimiento", poner("ejercicios.e4.solucion.primer_cero_km", 10))
    obj("E4 · el origen a otra distancia", poner("ejercicios.e4.solucion.dist_origen_km", lambda v: v + 50))
    obj("E4 · cambio de β mal", poner("ejercicios.e4.solucion.cambio_beta_pct", lambda v: v * 2))
    obj("E4 · e^β que no es la exponencial de β", poner("ejercicios.e4.solucion.eb_400", lambda v: v * 1.01))
    obj("E5 · p por debajo del mínimo", poner("ejercicios.e5.solucion.envolvente_D.dclf_p", 0.005))
    obj("E5 · ~ G + D rechaza en el rango largo", poner("ejercicios.e5.solucion.envolvente_GD.dclf_p", 0.03))
    obj("E5 · ~ G + D no rechaza en el corto", poner("ejercicios.e5.solucion.envolvente_GD.dclf_p_corto", 0.2))
    obj("E5 · ~ D no rechaza en el corto", poner("ejercicios.e5.solucion.envolvente_D.dclf_p_corto", 0.3))
    obj("E5 · una semilla le da la vuelta", poner("ejercicios.e5.solucion.dclf_GD_otras_semillas.3", 0.04))
    obj("E5 · el rango citado no es el de las semillas", poner("ejercicios.e5.solucion.dclf_GD_rango.1", 0.3))
    obj("E5 · el rango por defecto mal", poner("ejercicios.e5.solucion.envolvente_GD.r_max_km", 100))
    obj("E5 · la z de D sobrevive", poner("ejercicios.e5.solucion.kppm.1.z_D", -2.5))
    obj("E5 · la z de G cae", poner("ejercicios.e5.solucion.kppm.0.z_G", 1.2))
    obj("E5 · σ de Kinhom mal", poner("ejercicios.e5.solucion.sigma_kinhom_km", lambda v: v * 1.1))
    obj("E5 · con la λ del modelo rechaza el largo",
        poner("ejercicios.e5.solucion.envolvente_GD_lambda.dclf_p", 0.03))
    obj("E5 · la varianza no crece", poner("ejercicios.e5.solucion.varianza.veces", 0.5))

    # ---- familia 2 · sincronía ---------------------------------------
    obj("una cifra reutilizada cambiada en el preparcial",
        poner("reutilizado.c4m1_factor.valor", lambda v: v * 1.01))
    obj("el capítulo 4 se regenera debajo", poner("m1.factor_lambda", lambda v: v * 1.01), "cap4_datos.json")
    obj("el capítulo 5 mueve su media del modelo", poner("m10.curva.mmean.10", lambda v: v * 1.5), "cap5_datos.json")
    for g, serie in (("g_hist", "observado"), ("g_supuesto", "esperanza_min"), ("g_pcf", "g"),
                     ("g_pico", "maximo"), ("g_kinhom", "observada"), ("g_dos", "csr_observada")):
        obj(f"gráfico {g}: una serie movida", poner(f"graficos.{g}.{serie}.3", lambda v: v * 1.2))
    obj("gráfico g_supuesto: el rectángulo movido", poner("graficos.g_supuesto.rectangulo.2", lambda v: v * 1.2))
    obj("gráfico g_pcf: la lectura de 3 km movida", poner("graficos.g_pcf.forma.lectura.g", lambda v: v + 0.1))
    obj("gráfico g_pcf: el disco movido", poner("graficos.g_pcf.forma.lectura.disco", lambda v: v + 0.1))
    obj("gráfico g_dos: lo que se lleva la intensidad, mal",
        poner("graficos.g_dos.forma.llevado_primera_pct", lambda v: v * 2))
    D.append(("se regenera el JSON y no se reensambla", "datos", "obj_solo",
              poner("nuevo.tope_ppl.lado_x_m", 3001)))
    fun("el HTML no incrusta el JSON",
        lambda t: t.replace("const DATOS_PRE2 = ", "const OTROS_DATOS = ", 1))

    # ---- familias 3, 4 y 5 · las preguntas (HTML) --------------------
    fun("se pierde la pregunta del módulo 4.1", quita_pregunta)
    txt("un repaso con el título cambiado", "Cap. 4 · módulo 7 — Las funciones G y F",
        "Cap. 4 · módulo 7 — Las funciones F y G")
    txt("un repaso que enlaza a otro archivo",
        'href: "capitulo-5-intensidad-nucleos.html" }', 'href: "capitulo-4-patrones-puntuales.html" }')
    fun("una opción sin retro",
        lambda t: re.sub(r'(correcta: false,\n            retro: )"(?:[^"\\]|\\.)*"', r'\1""', t, count=1))
    fun("dos retros iguales en una pregunta", lambda t: _retros_iguales(t))
    fun("dos correctas en una de opción única", lambda t: _dos_correctas(t))
    fun("el bloque C pierde su gráfico",
        lambda t: _cambia_tipo_bloque(t, "bloque-c", "grafico", "opcion"))
    fun("una retro nombra una posición",
        lambda t: re.sub(r'(correcta: false,\n            retro: ")', r"\1Como las dos primeras, ", t, count=1))
    fun("un enunciado contiene su clave", lambda t: _enunciado_con_clave(t))
    fun("una clave mucho más larga", lambda t: _clave_larga(t))
    fun("la correcta siempre delante", correctas_delante)
    fun("la correcta siempre la más larga", correctas_largas)
    fun("una descripción de gráfico con entidades",
        lambda t: t.replace('descripcionGrafico: "Barras:', 'descripcionGrafico: "Barras&nbsp;:', 1))

    # ---- familia 6 · ejercicios --------------------------------------
    obj("e2 · una respuesta pierde su ancla",
        poner("ejercicios.e2.solucion.respuestas.0.pide", "di algo que el enunciado no pide"))
    obj("e3 · una demanda se queda sin respuesta",
        lambda o: o["ejercicios"]["e3"]["solucion"]["respuestas"].pop())
    obj("e4 · una cifra a mano en una respuesta",
        poner("ejercicios.e4.solucion.respuestas.1.respuesta",
              lambda v: v.replace("El de kilómetros.", "El de kilómetros, con 123.45 de margen.")))
    obj("e5 · un módulo fuera del alcance",
        poner("ejercicios.e5.modulos", ["cap5.m10", "cap3.m2"]))
    fun("la página pierde un ejercicio", quita_ejercicio)

    # ---- familia 7 · catálogo ----------------------------------------
    obj("un error cita una cifra que no existe",
        poner("errores.0.claves", ["c4m1_lambda_urb", "no_existe"]))
    obj("el catálogo pierde un error", lambda o: o["errores"].pop())
    txt("la página pierde el título de un error",
        "<h3>Publicar una intensidad sin su ventana</h3>", "<h3>Otra cosa</h3>")

    # ---- la fuente primaria de los ejercicios ------------------------
    fun("Murchison pierde un yacimiento",
        lambda t: "\n".join(t.splitlines()[:-1]) + "\n", "preparcial2_murchison_oro.csv")
    fun("Murchison: las fallas desplazadas",
        lambda t: _desplaza_falla(t), "preparcial2_murchison_fallas.csv")
    fun("Murchison: un vértice del greenstone movido",
        lambda t: _mueve_vertice(t), "preparcial2_murchison_greenstone.csv")
    fun("Murchison: la ventana más ancha",
        lambda t: t.replace("682.5896", "690.5896"), "preparcial2_murchison_ventana.csv")
    return D


def _primera_pregunta_unica(t):
    """La posición del bloque `opciones` de la primera pregunta de opción
    única del bloque A."""
    i = t.index("AUTOEVALUACIONES['bloque-a'] = [")
    j = t.index('tipo: "opcion"', i)
    k = t.index("        opciones: [\n", j)
    fin = t.index("\n        ]", k)
    return k, fin


def _retros_iguales(t):
    k, fin = _primera_pregunta_unica(t)
    bloque = t[k:fin]
    retros = re.findall(r'retro: ("(?:[^"\\]|\\.)*")', bloque)
    nuevo = bloque.replace(retros[1], retros[0], 1)
    return t[:k] + nuevo + t[fin:]


def _dos_correctas(t):
    k, fin = _primera_pregunta_unica(t)
    bloque = t[k:fin].replace("correcta: false", "correcta: true", 1)
    return t[:k] + bloque + t[fin:]


def _cambia_tipo_bloque(t, bloque, de, a):
    i = t.index(f"AUTOEVALUACIONES['{bloque}'] = [")
    j = t.index(f'tipo: "{de}"', i)
    return t[:j] + f'tipo: "{a}"' + t[j + len(f'tipo: "{de}"'):]


def _enunciado_con_clave(t):
    k, fin = _primera_pregunta_unica(t)
    clave = re.search(r'\{ texto: ("(?:[^"\\]|\\.)*"), correcta: true', t[k:fin]).group(1)
    i = t.rindex("pregunta: ", 0, k)
    j = t.index("\n", i)
    linea = t[i:j]
    nueva = linea[:-2] + " " + json.loads(clave) + '",' if linea.endswith('",') else linea
    return t[:i] + nueva + t[j:]


def _clave_larga(t):
    k, fin = _primera_pregunta_unica(t)
    bloque = re.sub(r'(\{ texto: "(?:[^"\\]|\\.)*?)(", correcta: true)',
                    r"\1, dicho con muchísimas más palabras de las necesarias\2", t[k:fin], count=1)
    return t[:k] + bloque + t[fin:]


def _desplaza_falla(t):
    """Todas las fallas, 5 km al este: desplazar una sola no mueve ningún
    percentil, y la inyección no probaba nada (primera corrida del arnés)."""
    filas = t.splitlines()
    fuera = [filas[0]]
    for f in filas[1:]:
        v = f.split(",")
        v[0], v[2] = str(float(v[0]) + 5), str(float(v[2]) + 5)
        fuera.append(",".join(v))
    return "\n".join(fuera) + "\n"


def _mueve_vertice(t):
    filas = t.splitlines()
    c = filas[2].split(",")
    c[3] = str(float(c[3]) + 3)
    filas[2] = ",".join(c)
    return "\n".join(filas) + "\n"


# =====================================================================
# El banco de pruebas
# =====================================================================
def corre(rutas):
    entorno = dict(os.environ)
    entorno["PREPARCIAL2_DATOS"] = str(rutas["datos"])
    entorno["PREPARCIAL2_HTML"] = str(rutas["html"])
    entorno["PREPARCIAL2_CAPS"] = str(rutas["caps"])
    entorno["PREPARCIAL2_MURCHISON"] = str(rutas["murch"])
    res = subprocess.run([PY, str(AUDITOR)], capture_output=True, text=True, cwd=str(RAIZ), env=entorno)
    return res.returncode, res.stdout + res.stderr


def resumen(salida):
    """El recuento del CIERRE, no el de la primera familia: la primera
    versión leía este y daba «0 fallos» en defectos cazados."""
    m = re.findall(r"\n  (\d+ comprobaciones · \d+ fallos)", salida)
    return m[-1] if m else "(sin resumen)"


def revento(salida):
    return "Traceback (most recent call last)" in salida


def nombres(salida, estado):
    fuera = set()
    for linea in salida.splitlines():
        m = re.match(r"\s{2}" + re.escape(estado) + r"\s{2,}(\S.*?)\s{2,}", linea + "  ")
        if m:
            fuera.add(m.group(1).strip())
    return fuera


def tipo_de(n):
    n = re.sub(r"\d+×\d+", "k×k", n)
    n = re.sub(r"^e\d ·", "eN ·", n)
    n = re.sub(r"^gráfico g_\w+", "gráfico", n)
    n = re.sub(r"^bloque-\w", "bloque", n)
    n = re.sub(r"envolvente_\w+", "envolvente", n)
    n = re.sub(r"\b\d+ cifras\b", "N cifras", n)
    return n


def main() -> int:
    publicados = [DATOS, HTML] + [SALIDAS / c for c in CAPS] + [SALIDAS / m for m in MURCH]
    faltan = [p for p in publicados if not p.exists()]
    if faltan:
        print("PARADO: faltan " + ", ".join(str(p) for p in faltan))
        return 1
    originales = {p: p.read_bytes() for p in publicados}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="prueba_auditor_preparcial2_"))
    limpio = {"datos": tmp / DATOS.name, "html": tmp / HTML.name, "caps": tmp / "caps", "murch": tmp / "murch"}
    shutil.copy(DATOS, limpio["datos"])
    shutil.copy(HTML, limpio["html"])
    limpio["caps"].mkdir()
    limpio["murch"].mkdir()
    for c in CAPS:
        shutil.copy(SALIDAS / c, limpio["caps"] / c)
    for m in MURCH:
        shutil.copy(SALIDAS / m, limpio["murch"] / m)

    print("=" * 74)
    print("  prueba_auditor_preparcial2.py — el arnés de inyección del preparcial II")
    print("=" * 74)
    codigo, salida = corre(limpio)
    print(f"\n  {'OK ' if codigo == 0 else 'MAL'}  control de entrada · sin inyectar nada")
    print(f"        {resumen(salida)}")
    if codigo != 0:
        print("\n  PARADO: el control falla, así que el arnés no prueba nada.")
        return 1
    todas = nombres(salida, "OK ")
    vistas = set()
    lista = defectos()
    cazados = inertes = reventados = 0
    print(f"\n  {len(lista)} defectos que inyectar\n" + "-" * 74)
    for nombre, destino, tipo, accion in lista:
        rutas = dict(limpio)
        if destino in ("datos", "html"):
            origen = limpio[destino]
            roto = tmp / f"roto_{origen.name}"
        else:
            carpeta = "caps" if destino in CAPS else "murch"
            nueva = tmp / f"{carpeta}_rotos"
            if nueva.exists():
                shutil.rmtree(nueva)
            shutil.copytree(limpio[carpeta], nueva)
            rutas[carpeta] = nueva
            origen = roto = nueva / destino
        texto = origen.read_text(encoding="utf-8")
        solo_json = tipo == "obj_solo"
        if solo_json:
            tipo = "obj"
        if tipo == "obj":
            o = json.loads(texto)
            antes = json.dumps(o, ensure_ascii=False, sort_keys=True)
            accion(o)
            if json.dumps(o, ensure_ascii=False, sort_keys=True) == antes:
                print(f"  MAL  {nombre}\n        INERTE · la mutación no cambió el archivo")
                inertes += 1
                continue
            nuevo = json.dumps(o, ensure_ascii=False)
        elif tipo == "txt":
            busca, pone = accion
            if busca not in texto:
                print(f"  MAL  {nombre}\n        INERTE · no aparece {busca[:50]!r}")
                inertes += 1
                continue
            nuevo = texto.replace(busca, pone, 1)
        else:
            nuevo = accion(texto)
        if nuevo == texto:
            print(f"  MAL  {nombre}\n        INERTE · la sustitución no cambió nada")
            inertes += 1
            continue
        roto.write_text(nuevo, encoding="utf-8")
        if destino in ("datos", "html"):
            rutas[destino] = roto
        # Una inyección en el JSON se copia también al JSON incrustado en el
        # HTML: si no, la que falla SIEMPRE es la sincronía —el HTML lleva el
        # original— y nunca se sabe si la comprobación atacada funciona. La
        # única que no se copia es la que prueba esa sincronía.
        if destino == "datos" and not solo_json:
            h = limpio["html"].read_text(encoding="utf-8")
            i = h.index("    const DATOS_PRE2 = ") + len("    const DATOS_PRE2 = ")
            j = h.index(";\n", i)
            h_roto = tmp / "roto_sincronizado.html"
            h_roto.write_text(h[:i] + json.dumps(json.loads(nuevo), ensure_ascii=False) + h[j:], encoding="utf-8")
            rutas["html"] = h_roto
        codigo, salida = corre(rutas)
        murio = revento(salida)
        # Cazado = el auditor terminó, informó, y nombró al menos una
        # comprobación en rojo. Un código distinto de cero sin ninguna línea
        # MAL es un auditor que se paró antes de llegar a mirar.
        fallidas = sorted(nombres(salida, "MAL"))
        ok = codigo != 0 and not murio and bool(fallidas)
        cazados += ok
        reventados += murio
        print(f"  {'MAL' if murio or not ok else 'OK '}  {nombre}")
        print(f"        {'REVENTÓ · el auditor murió, no informó' if murio else resumen(salida)}"
              + ("" if murio else f" · {'; '.join(x[:40] for x in fallidas[:2])}"))
        if murio:
            print("        " + salida.strip().splitlines()[-1][:110])
        vistas |= nombres(salida, "MAL")

    codigo, salida = corre(limpio)
    print("-" * 74)
    print(f"  {'OK ' if codigo == 0 else 'MAL'}  control de salida")
    intactos = all(p.read_bytes() == b for p, b in originales.items())
    print(f"  {'OK ' if intactos else 'MAL'}  los publicados siguen byte a byte igual ({len(originales)} archivos)")
    avisa_rotulos_largos(todas)
    tipos_todos = {tipo_de(x) for x in todas}
    tipos_vistos = {tipo_de(x) for x in vistas} & tipos_todos
    nunca = sorted(tipos_todos - tipos_vistos)
    print("\n" + "=" * 74)
    print(f"  {cazados} de {len(lista)} defectos cazados"
          + (f"  ({inertes} inertes)" if inertes else "")
          + (f"  ({reventados} reventaron al auditor)" if reventados else ""))
    print(f"  instancias: {len(vistas & todas)} de {len(todas)} se han visto fallar")
    print(f"  TIPOS:      {len(tipos_vistos)} de {len(tipos_todos)} se han visto fallar")
    if nunca:
        print(f"\n  {len(nunca)} tipo(s) que este arnés todavía no ataca:")
        for t in nunca:
            print(f"      · {t}")
    print("=" * 74)
    shutil.rmtree(tmp, ignore_errors=True)
    bien = cazados == len(lista) and not inertes and not reventados and codigo == 0 and intactos
    print(f"\n  {'Auditor del preparcial del Corte II verificado.' if bien else 'ARNÉS EN ROJO.'}")
    return 0 if bien else 1


if __name__ == "__main__":
    sys.exit(main())
