#!/usr/bin/env python3
"""
ensambla_preparcial2.py — construye el preparcial del Corte II

Material de Estadística Espacial 2026-II (20929).
Ver PLAN_Preparcial_Corte_2.md.

Siete módulos: qué entra en el parcial, los bloques A (capítulo 4) y B
(capítulo 5), seis rutinas con salida ejecutada, el bloque C que cruza los
dos capítulos, los cinco ejercicios sobre el oro de Murchison y el catálogo
de errores que se repiten. Es `ensambla_preparcial1.py` con otro temario, y
hereda sus reglas, sus guardas y sus lecciones; las que cambian se dicen
donde viven.

LOS MÓDULOS SE NUMERAN SOLOS. Hay una lista ordenada de constructores
(`CONSTRUCTORES`, al final) y el número, la cabecera y la entrada de
navegación salen de la posición. Un botón que abre un `template` inexistente
deja el panel en blanco sin un solo error en consola.

NINGUNA CIFRA A MANO (D10). Todas entran por `cifra()`, que las saca de
`preparcial2_datos.json`; el JSON guarda de qué archivo y de qué ruta vino
cada una para que `audita_preparcial2.py` pueda volver a resolverlas. Lo
único que este archivo decide sobre una cifra es cuántos decimales y qué
unidad se le ponen al mostrarla. Y las glosas verbales —«trece veces», «la
mitad»— también son cifras: o se citan por su clave, o no se dicen.

DOS GUARDAS QUE EL CORTE I NO TENÍA AL NACER, y las dos salen de su §13:

  · **la clave no puede ser la opción más larga por goleada.** El banco del
    Corte I se contestaba al 92 % sin saber nada eligiendo la más larga; la
    regla `len(clave) − max(len(distractores)) > 20` lo habría cazado entero.
  · **ninguna cifra reutilizada puede quedarse sin citar.** Un campo del
    JSON que ninguna página lee suele ser una advertencia que nunca llegó a
    escribirse (el `caso_aviso` del capítulo 1).

LOS SEIS BLOQUES DE CÓDIGO SE EJECUTARON PARA ESCRIBIR SUS `#>`, y
`verifica_bloques.py` los vuelve a ejecutar encadenados. Van CONCATENADOS y
no interpolados: el intérprete del proyecto es 3.10 y una f-string no admite
una barra invertida dentro de su expresión.

Uso:  python3 precalculo/ensambla_preparcial2.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import random
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"
sys.path.insert(0, str(RAIZ / "precalculo"))
import alcance_preparcial2 as ALC  # noqa: E402


def _ruta(var: str, defecto: pathlib.Path) -> pathlib.Path:
    """La ruta publicada, o la copia que apunte la variable de entorno: es lo
    que deja al arnés de inyección construir desde un JSON envenenado sin
    escribir jamás sobre lo publicado."""
    p = pathlib.Path(os.environ.get(var) or defecto)
    if var.endswith("DESTINO"):
        return p
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return p


PLANTILLA = _ruta("PREPARCIAL2_PLANTILLA", RAIZ / "plantilla" / "plantilla-capitulo.html")
DESTINO = _ruta("PREPARCIAL2_DESTINO", RAIZ / "Htmls_Espacial" / "preparcial-corte-2.html")
D = json.loads(_ruta("PREPARCIAL2_DATOS", SALIDAS / "preparcial2_datos.json")
               .read_text(encoding="utf-8"))

meta, REU, ERRORES, EJ = D["meta"], D["reutilizado"], D["errores"], D["ejercicios"]
GR, NV = D["graficos"], D["nuevo"]


# ---------------------------------------------------------------------
# Formateadores. Los nombres que `sin_aritmetica.py` vigila.
# ---------------------------------------------------------------------
def n(x, d=5):
    """Punto decimal, la regla del material desde el 2026-08-03. El signo
    menos es el tipográfico (U+2212), el mismo de las fórmulas: con guion,
    «-0.02426» y «L(r) − r» convivían en la misma página."""
    return f"{float(x):.{d}f}".replace("-", "−")


def n5(x):
    return n(x, 5)


def ent(x):
    """Entero con separador de millar fino (U+202F)."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def cien(x):
    """Notación científica corta, para las cifras que con decimales fijos se
    publicarían como «0.00000»: el número de condición de una matriz
    singular es la cifra que el módulo 9 enseña, y redondeada a cero
    afirmaría lo contrario."""
    return f"{float(x):.3e}"


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def val(clave):
    if clave not in REU:
        sys.exit(f"PARADO: la cifra «{clave}» no está en preparcial2_datos.json")
    return REU[clave]["valor"]


def que(clave):
    return REU[clave]["que"]


def val_nuevo(ruta):
    cur = NV
    for parte in ruta.split("."):
        if not isinstance(cur, dict) or parte not in cur:
            sys.exit(f"PARADO: la ruta «{ruta}» no existe en nuevo")
        cur = cur[parte]
    return cur


# ---------------------------------------------------------------------
# Cómo se muestra cada cifra citada: decimales y unidad. Es presentación,
# no cálculo. `"e"` en vez de un número de decimales pide notación
# científica (ver `cien`).
# ---------------------------------------------------------------------
# Nada se pega: el porcentaje va separado por un espacio fino como en los
# capítulos («un 4.79355 %»), y el grado no aparece en este temario.

PRESENTA = {
    # --- capítulo 4 ---
    "c4m1_n_urb": (0, ""), "c4m1_n_dc": (0, ""),     "c4m1_area_urb": (5, "km²"), "c4m1_area_dc": (5, "km²"),
    "c4m1_lambda_urb": (5, "sedes/km²"), "c4m1_lambda_dc": (5, "sedes/km²"),
    "c4m1_factor": (5, ""),
    "c4m1_total": (0, ""), "c4m1_fuera_urb": (0, ""), "c4m1_fuera_dc": (0, ""),
    "c4m8_peso_1km": (2, ""), "c4m8_peso_rmax": (2, ""), "c4m8_peso_doble": (2, ""),
    "c4m8_peso_doble_max": (1, ""),
    "c4m2_celdas": (0, ""), "c4m2_media": (5, ""), "c4m2_dispersion": (5, ""),
    "c4m2_disp_nula": (1, ""), "c4m2_vacios": (0, ""), "c4m2_maximo": (0, ""),
    "c4m2_esp_baja": (0, ""), "c4m2_chi2": (2, ""), "c4m2_gl": (0, ""),
    "c4m2_esp_min": (2, ""), "c4m2_esp_max": (1, ""),
    "c4m3_ce_bog": (5, ""), "c4m3_nn_bog": (2, "m"), "c4m3_nn_esp_bog": (2, "m"),
    "c4m4_n_real": (0, ""), "c4m4_lambda": (0, ""), "c4m4_media": (3, ""),
    "c4m4_var": (3, ""),     "c4m4_R_media": (5, ""), "c4m4_R_bajo1": (0, ""),         "c4m5_chi2": (6, ""), "c4m5_gl": (0, ""), "c4m5_ce_orig": (5, ""), "c4m5_ce_reb": (5, ""),
    "c4m6_red_rechazos": (0, ""), "c4m6_red_emin10": (2, ""),
    "c4m7_umbral_f": (1, ""), "c4m7_f_sitios": (0, ""), "c4m7_f_rejilla": (0, ""),
    "c4m8_vecino_max": (0, "m"), "c4m8_rmax": (0, "m"), "c4m8_max_desvio": (2, "m"),
    "c4m8_vecinas": (2, ""), "c4m8_vecinas_csr": (2, ""),
    "c4m9_g_max": (5, ""), "c4m9_g_final": (5, ""),
    "c4m9_r_final": (0, "m"),
    "c4m10_veces_iso": (0, ""), "c4m10_vertices": (0, ""), "c4m10_sesgo": (1, "%"),
    "c4m10_horas_iso": (1, "horas"), "c4m10_min_trans": (1, "minutos"),
    "c4m11_tasa_bog": (1, "%"), "c4m11_nivel": (2, ""),
    "c4m11_nsim": (0, ""), "c4m11_p_min": (3, ""),
    # --- capítulo 5 ---
    "c5m1_n_ken": (0, ""), "c5m1_area_ken": (2, "km²"), "c5m1_lambda_ken": (2, "sedes/km²"),
    "c5m2_caida": (1, "%"), "c5m2_nucleo_dif": (1, "%"),
    "c5m3_tope_jp": (4, ""), "c5m3_razon_urb": (5, ""),
    "c5m4_n": (0, ""), "c5m4_sigma_800": (0, "m"), "c5m4_masa_def": (2, ""),
    "c5m4_masa_sin": (2, ""), "c5m4_masa_dig": (2, ""),     "c5m4_exceso": (2, "%"),
    "c5m5_n_of": (0, ""), "c5m5_n_11": (0, ""), "c5m5_pct_11": (1, "%"),
    "c5m5_total_est": (0, ""), "c5m5_cor_of_11": (3, ""), "c5m5_cor_of_es": (3, ""),
    "c5m5_cor_11_es": (3, ""),
    "c5m6_ch_pmax": (5, ""), "c5m6_ch_global": (5, ""), "c5m6_ch_casos": (0, ""),
    "c5m6_ch_controles": (0, ""), "c5m6_orient_ch": (2, ""), "c5m6_orient_bog": (2, ""),
    "c5m7_bei_n": (0, ""), "c5m7_razon_bog": (4, ""), "c5m7_bulto_bog": (5, ""),
        "c5m8_suma_pesos": (5, "km²"), "c5m8_area": (5, "km²"), "c5m8_sin_contar": (5, "km²"),
    "c5m8_esperadas": (2, ""), "c5m8_gana_ppm": (5, ""), "c5m8_gana_const": (5, ""),
    "c5m9_xc": (5, ""), "c5m9_yc": (5, ""), "c5m9_z_xc": (2, ""), "c5m9_z_yc": (2, ""),
    "c5m9_cond": ("e", ""), "c5m9_mejora": (0, "veces"),
    "c5m10_pct_fuera": (0, "%"), "c5m10_primer": (0, "m"), "c5m10_ultimo": (0, "m"),
    "c5m10_rmax": (0, "m"), "c5m10_nodos_dentro": (0, ""), "c5m10_tasa": (1, "%"),
    "c5m10_nivel": (1, "%"), "c5m10_dclf": (3, ""), "c5m10_fuera": (0, ""),
    "c5m11_th_iso_esc": (0, "m"), "c5m11_th_tr_esc": (0, "m"), "c5m11_th_iso_mu": (1, ""),
    "c5m11_th_tr_mu": (1, ""), "c5m11_mat_iso_mu": (1, ""), "c5m11_th_iso_seg": (1, "s"), "c5m11_th_tr_seg": (2, "s"),
    "c5m11_mu_pct": (1, "%"), "c5m11_deff": (5, ""), "c5m11_n": (0, ""),
    "c5m11_neff": (5, ""), "c5m11_mat_iso_inf": (5, ""), "c5m11_z_pois": (2, ""),
    "c5m11_z_th_tr": (2, ""), "c5m11_zc": (2, ""), "c5m11_dup_cambio": (1, "%"),
    # --- los cálculos nuevos, por su ruta dentro de `nuevo` ---
    "ce_ventana.ce_dc": (5, ""), "ce_ventana.nn_dc": (2, "m"), "ce_ventana.nn_esp_dc": (2, "m"),
    "rebarajado.chi2_10_orig": (2, ""), "rebarajado.chi2_10_reb": (2, ""),
    "nrank.nsim": (0, ""), "nrank.nivel_pct": (0, "%"), "nrank.correcto": (0, ""),
    "nrank.nivel_defecto_pct": (0, "%"), "nrank.p_minimo": (3, ""),
    "tope_ppl.lado_x_m": (0, ""), "tope_ppl.lado_y_m": (0, ""), "tope_ppl.correcto": (0, "m"),
    "tope_ppl.csr_realizaciones": (0, ""), "tope_ppl.csr_chocan_en_el_tope": (0, ""),
        "niveles.cap4_pct": (0, "%"),
    "riesgo_relativo.correcto": (5, ""),
    "forzado.n": (0, ""), "forzado.area_km2": (5, "km²"), "forzado.suma_pesos_km2": (5, "km²"),
    "forzado.sin_contar_km2": (5, "km²"), "forzado.correcto": (3, ""),
    "n_efectivo.efecto_diseno": (5, ""),
    "n_efectivo.correcto": (2, ""),
    "resto_dc.n_resto": (0, ""), "resto_dc.area_resto_km2": (2, "km²"),
    "resto_dc.lambda_resto_km2": (5, "sedes/km²"), "resto_dc.correcto": (1, ""),
    "denso.lambda": (0, ""), "denso.R_media": (5, ""), "denso.sesgo": (5, ""),
    "denso.sesgo_capitulo": (5, ""), "denso.R_bajo1": (0, ""), "denso.n_real": (0, ""),
    "denso.pct_bajo1": (2, "%"), "denso.pct_bajo1_capitulo": (2, "%"), "denso.R_sd": (5, ""),
    "denso.n_media": (1, ""), "denso.n_var": (1, ""),
    "traslacion.d_corta_m": (0, "m"), "traslacion.d_larga_m": (0, "m"),
    "traslacion.frac_este_100": (2, "%"), "traslacion.frac_norte_100": (2, "%"),
    "traslacion.peso_este_100": (4, ""), "traslacion.peso_norte_100": (4, ""), "traslacion.peso_este_1000": (4, ""),
    "escalas.thomas_media_m": (0, "m"), "escalas.matern_media_m": (0, "m"),
    "niveles.cap4_cobertura_pct": (0, "%"),
    "c5m11_mat_iso_esc": (0, "m"), "c5m11_z_abs_max": (2, ""),     "c5m6_bog_global": (2, ""), "c5m10_veces_nivel": (1, ""), "c5m10_nsim": (0, ""),
    "supuesto_rw.rechazos_sin_supuesto": (0, ""),
    "c4m4_R_sd": (5, ""), "c4m8_parejas": (0, ""), "c4m10_r_sesgo": (0, "m"),
    # --- ronda 4 de la auditoría (2026-10-05) ---
    "c5m10_mmean_pct": (3, "%"), "c5m11_repetidas": (0, ""),
    "limite.corregida_min_km2": (4, "sedes/km²"), "limite.corregida_max_km2": (4, "sedes/km²"),
    "tope_ppl.csr_puntos_esperados": (0, ""), "tope_ppl.csr_no_chocan": (0, ""),
    "tope_ppl.csr_sigma_min_m": (0, "m"), "tope_ppl.csr_sigma_max_m": (0, "m"),
    "gf_suecos.n": (0, ""), "gf_suecos.lado_x_m": (1, ""), "gf_suecos.lado_y_m": (0, "m"),
    "gf_suecos.g_mediana_m": (3, "m"), "gf_suecos.f_mediana_m": (3, "m"),
    "gf_suecos.csr_mediana_m": (3, "m"), "iso_tras.max_dif_pct": (1, "%"), "iso_tras.r_max_dif_m": (0, "m"), "gf_suecos.j_nodos": (0, ""),
    "ebeta.pct_por_km": (2, "%"), "ebeta.factor_por_km": (3, ""),
    "kinhom_nucleo.sigma_nucleo_m": (0, "m"), "nrank.nivel": (2, ""),
    "c5m11_th_iso_inf": (2, ""), "c5m11_th_tr_inf": (2, ""),
}

USADAS = set()


def cifra(clave, v=None):
    """El valor de una cifra citada, ya vestido para leerse. El espacio entre
    número y unidad es `&nbsp;` (no se parte al final de una línea), salvo
    el porcentaje, que va pegado como en los capítulos."""
    if clave not in PRESENTA:
        sys.exit(f"PARADO: «{clave}» se cita sin decir con cuántos decimales "
                 f"ni en qué unidad se muestra (añádela a PRESENTA)")
    USADAS.add(clave)
    decimales, unidad = PRESENTA[clave]
    if v is None:
        v = val(clave)
    if isinstance(v, bool):
        return "sí" if v else "no"
    if decimales == "e":
        texto = cien(v)
    elif decimales == 0:
        texto = ent(v)
    else:
        texto = n(v, decimales)
    return f"{texto}&nbsp;{unidad}" if unidad else texto


def cn(ruta):
    """Una cifra de los cálculos nuevos, por su ruta dentro de `nuevo`."""
    return cifra(ruta, val_nuevo(ruta))


def dist(item, id_, decimales=None):
    """El valor de un distractor calculado, por su identificador."""
    it = val_nuevo(item)
    d = it["decimales"] if decimales is None else decimales
    for x in it["distractores"]:
        if x["id"] == id_:
            return ent(x["valor"]) if d == 0 else n(x["valor"], d)
    sys.exit(f"PARADO: no hay distractor «{id_}» en {item}")


c = cifra


def enlace_modulo(doc, modulo, texto):
    """El enlace a un módulo de un capítulo — el único sitio donde se arma.
    Lleva a la portada del capítulo y nombra el módulo en el texto, como en
    el Corte I: la plantilla no tiene enlaces profundos."""
    return f'<a href="{ALC.DOCS[doc]}">{texto}</a>'


NOMBRE_CAP = {
    "cap4": "Capítulo 4 · Patrones puntuales: descripción, CSR y funciones de resumen",
    "cap5": "Capítulo 5 · Intensidad por núcleos y modelamiento de procesos puntuales",
}


def cabecera(num, titulo, ingles, objetivo):
    return f"""
  <!-- ============================================================ -->
  <!-- MÓDULO {num} · {titulo[:52]:<52} -->
  <!-- ============================================================ -->
  <template id="module-{num}">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo {num}</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">{titulo}
          <span class="text-gray-400 font-normal text-2xl">/ {ingles}</span></h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Qué se comprueba aquí</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">{objetivo}</p>
          </div>
        </div>
      </div>
"""


CIERRE = """    </div>
  </template>
"""


# =====================================================================
# LAS PREGUNTAS
#
# Cada una declara el módulo del CAPÍTULO que evalúa: de ahí sale el
# `repaso` del resumen. Toda opción lleva su `retro`, también las correctas,
# y las incorrectas dicen a qué error llevan.
#
# Y cada una tiene que aportar algo que las cinco superficies publicadas del
# Corte II no piden (§3 del plan): un ángulo nuevo, una transferencia o un
# cruce. El blueprint del §4 dice, pregunta por pregunta, cuál.
# =====================================================================
def op(texto, correcta, retro):
    return {"texto": texto, "correcta": correcta, "retro": retro}


def preg(tipo, doc, modulo, pregunta, pista, **kw):
    if not ALC.en_alcance(doc, modulo):
        sys.exit(f"PARADO: una pregunta apunta a {doc}.m{modulo}, fuera del alcance")
    q = {"tipo": tipo, "doc": doc, "modulo": modulo, "pregunta": pregunta, "pista": pista}
    q.update(kw)
    return q


# Las cifras que solo existen dentro de una serie de gráfico se leen aquí,
# por posición o por nombre, y se formatean con `n()`/`ent()`: son las
# mismas que el auditor resuelve contra el capítulo.
F_HIST = GR["g_hist"]["forma"]
SUP = GR["g_supuesto"]
EMIN = dict(zip(SUP["nx"], SUP["esperanza_min"]))
RESP = SUP["forma"]["respetan"]
NX = SUP["nx"]
# La primera rejilla del barrido en que la ciudad ya tiene una celda que espera
# menos de 5: la retro de A06 decía «con la 10 × 10 ya», y baja antes
# (verdad, ronda 5).
K_BAJA = next(k for k in NX if EMIN[k] < 5)
if K_BAJA == NX[0] or K_BAJA >= 10:
    sys.exit("PARADO: la ciudad ya no baja de 5 entre la primera rejilla y la 10 × 10")
PCF = GR["g_pcf"]
R1_PCF = next(r for r in PCF["r"] if r > 0)
# La descripción del gráfico del 4.9 dice que el valor más bajo de g es el del
# último nodo; si deja de serlo, se para en vez de describir otra curva.
if PCF["forma"]["r_g_min"] != PCF["r"][-1]:
    sys.exit("PARADO: el mínimo de g de las sedes ya no está en el último nodo del barrido")
# Y la del 5.2, que el pico baja con cada ancho, sin excepción.
if any(b >= a for a, b in zip(GR["g_pico"]["maximo"], GR["g_pico"]["maximo"][1:])):
    sys.exit("PARADO: el pico de Kennedy ya no baja con cada ancho, y la descripción lo afirma")
KIN = GR["g_kinhom"]
PICO = GR["g_pico"]


def sig2(x):
    """Dos cifras significativas por debajo de 1 y dos decimales por encima:
    con decimales fijos, las esperanzas más pequeñas del barrido salían
    «0.00» en la descripción del gráfico, y son positivas (la escala es
    logarítmica)."""
    # `#` conserva los ceros significativos: con `.2g`, 0.1029 salía «0.1»
    # en el texto alternativo y «0.10» en las retros (auditoría, ronda 4).
    return n(x, 2) if x >= 1 else f"{float(x):#.2g}"


def ej(k):
    """«5 × 5», escrito a partir de un número de celdas por lado que vive en
    el JSON. Es presentación: el número no se calcula aquí."""
    return f"{ent(k)}&nbsp;×&nbsp;{ent(k)}"


# ---------------------------------------------------------------------
# BLOQUE A · capítulo 4
#
# Reescrito tras la auditoría de contenido del 2026-10-03 (§11 del plan):
# A1, A4, A6, A9 y A10 cambian de ángulo porque repetían un ítem ya
# publicado (el banco del Taller 2, un ejercicio guiado o una afirmación
# falsa copiada palabra por palabra); las demás se reescriben para que la
# forma no delate la clave —pistas sin las palabras de la correcta,
# distractores con salvedad, arranques iguales— y para que lo que afirman
# sea cierto también donde la primera versión exageraba.
# ---------------------------------------------------------------------
LEC = PCF["forma"]["lectura"]
# Los radios que el texto alternativo del 4.9 lee de la curva: los nodos más
# cercanos a cada kilómetro. Es selección de nodos, no cálculo de cifras.
NODOS_PCF = [min(range(len(PCF["r"])), key=lambda i, d=d: abs(PCF["r"][i] - d))
             for d in (1000, 2000, 3000, 4000, 5000)]
RECT = SUP["rectangulo"]
RECT_K = dict(zip(SUP["nx"], RECT))

BLOQUE_A = [
    preg("numerica", "cap4", 1,
         f"El Distrito Capital tiene {c('c4m1_n_dc')} sedes en {c('c4m1_area_dc')}; su perímetro "
         f"urbano, contenido en el Distrito, tiene {c('c4m1_n_urb')} en {c('c4m1_area_urb')}. "
         f"¿Cuántas veces es mayor la intensidad del perímetro urbano que la del resto del Distrito, "
         f"el suelo del D.C. que queda fuera del perímetro? Da el cociente con un decimal; se acepta "
         f"una diferencia de {n(0.5, 1)}.",
         "Una intensidad es siempre de una ventana: ¿cuál es aquí la del resto?",
         # La respuesta que se muestra tras el segundo fallo, con los decimales
         # que pide el enunciado: con todos, «71.19619252» dejaba sin saber si
         # 71.2 valía (auditoría de redacción, ronda 4).
         respuesta=float(cn('resto_dc.correcto')), tolerancia=0.5,
         retroAcierto=(
             f"El resto del Distrito tiene {cn('resto_dc.n_resto')} sedes en "
             f"{cn('resto_dc.area_resto_km2')}: {cn('resto_dc.lambda_resto_km2')}, frente a "
             f"{c('c4m1_lambda_urb')} en la ciudad, {cn('resto_dc.correcto')} veces menos. La λ del "
             f"D.C., {c('c4m1_lambda_dc')}, promedia dos zonas que no se parecen —la ciudad y el "
             f"suelo rural— y no describe ninguna: una intensidad vale para su ventana, y cambiar de "
             f"ventana mueve n y |W| a la vez."),
         retroFallo=(
             f"Si respondiste {dist('resto_dc', 'el_del_dc')}, comparaste con el Distrito entero, que "
             f"incluye la propia ciudad. Si respondiste {dist('resto_dc', 'area_entera')}, dividiste "
             f"las sedes del resto por el área de todo el Distrito. El resto es otra ventana: sus sedes "
             f"son las del D.C. menos las urbanas, y su área, la del D.C. menos la urbana. Es lo que "
             f"hace <code>ppp()</code> con cada ventana: cuenta solo las sedes que caen dentro y "
             f"descarta las demás con un aviso que nadie lee.")),

    preg("grafico", "cap4", 2,
         f"Las barras dan cuántas de las {c('c4m2_celdas')} celdas vivas —las que tienen algo de "
         f"área dentro del perímetro urbano— de la rejilla {ej(10)} tienen cada número de sedes. La "
         f"línea da cuántas lo tendrían si todas esperaran la media, {c('c4m2_media')} sedes, y los "
         f"conteos fueran Poisson. El índice de dispersión observado —varianza entre media de los "
         f"conteos— es {c('c4m2_dispersion')}. ¿Qué parte de ese índice pone el patrón de las sedes?",
         "Pregúntate si todas las celdas vivas esperan de verdad la media.",
         alto=250,
         descripcionGrafico=(
             f"Barras: cuántas celdas vivas tienen cada número de sedes, en tramos de "
             f"{ent(F_HIST['ancho_tramo'])}; hay {c('c4m2_vacios')} sin ninguna y la más "
             f"poblada tiene {c('c4m2_maximo')}. Con {ent(F_HIST['corte_bajo'])} sedes o menos "
             f"hay {ent(F_HIST['obs_hasta_10'])} celdas, y la línea pone "
             f"{sig2(F_HIST['ref_hasta_10'])}; con más de {ent(F_HIST['corte_alto'])}, "
             f"{ent(F_HIST['obs_desde_60'])} frente a {sig2(F_HIST['ref_desde_60'])}. Línea: "
             f"la Poisson de media {c('c4m2_media')}, concentrada alrededor de esa media."),
         dibujar="""canvas => {
            const g = DATOS_PRE2.graficos.g_hist;
            // Los tramos de hist() en R son cerrados por la derecha y el
            // primero incluye el 0: el de centro 32.5 cuenta de 31 a 35 sedes.
            const tramo = it => {
              const c = parseFloat(it.label), w = g.forma.ancho_tramo;
              const lo = Math.round(c - w / 2), hi = Math.round(c + w / 2);
              return (lo === 0 ? 'De 0' : 'De ' + (lo + 1)) + ' a ' + hi + ' sedes';
            };
            return crearGraficoLinea(canvas, g.centros.map(x => String(x)), [
              { type: 'bar', label: 'Celdas observadas', corto: 'Observadas', data: g.observado,
                backgroundColor: COLORES_GRAFICO.primario, borderWidth: 0, order: 2 },
              { label: 'Poisson de media común', corto: 'Poisson', data: g.referencia,
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent',
                cubicInterpolationMode: 'monotone', pointRadius: 0, borderWidth: 2, order: 1 }
            ], { scales: ejesPreparcial('Sedes por celda (centro del tramo)', 'Celdas'),
                 plugins: pluginsPreparcial(null, { titulo: tramo }) });
          }""",
         opciones=[
             op(f"Lo que va de unos {c('c4m2_disp_nula')} a {c('c4m2_dispersion')}: con estas celdas "
                f"recortadas, un Poisson homogéneo ya daría de media un índice de unos "
                f"{c('c4m2_disp_nula')}.", True,
                f"Es la idea central del módulo 2. La línea supone que todas las celdas esperan "
                f"{c('c4m2_media')} sedes, pero el perímetro recorta las del borde, y lo que cada una "
                f"espera —λ por su área dentro de la ventana— va de {c('c4m2_esp_min')} a "
                f"{c('c4m2_esp_max')} sedes. Con esperanzas tan desiguales, un Poisson homogéneo ya "
                f"daría de media un índice de unos {c('c4m2_disp_nula')}, no de 1: el patrón tiene que "
                f"explicar lo que sobra por encima. Por eso la línea del gráfico no es la referencia de "
                f"esta ventana: describe una rejilla de celdas iguales, todas con la misma esperanza."),
             op(f"Lo que va de 1 a {c('c4m2_dispersion')}: en un Poisson la varianza del conteo vale lo "
                f"mismo que su media, en las celdas enteras y en las recortadas.", False,
                f"Cada celda, sola, tiene la varianza igual a su media; pero el índice mezcla celdas que "
                f"esperan cosas distintas, de {c('c4m2_esp_min')} a {c('c4m2_esp_max')} sedes, y esa "
                f"mezcla ya hace la varianza de los conteos mayor que su media. Con estas celdas, un "
                f"Poisson homogéneo ya rondaría {c('c4m2_disp_nula')}: comparar con 1 le atribuye al "
                f"patrón lo que pone la ventana."),
             # La cifra de la gemela necesita un origen propio, falso: si solo la
             # clave decía de dónde sale el 15.2, la clave se elegía por eso
             # (forma, ronda 5).
             op(f"Lo que va de 1 a unos {c('c4m2_disp_nula')}: en celdas enteras, el agrupamiento de "
                f"las sedes ya daría un índice de unos {c('c4m2_disp_nula')}, y lo que pasa de ahí lo "
                f"ponen las celdas recortadas.", False,
                f"La atribución está al revés. Con estas celdas recortadas y λ constante, un Poisson "
                f"homogéneo ya rondaría {c('c4m2_disp_nula')}: ese tramo lo pone la ventana. Lo que "
                f"pasa de ahí, hasta {c('c4m2_dispersion')}, es lo que tiene que explicar el patrón."),
             op(f"Muy poca: con {c('c4m2_celdas')} celdas vivas, y {c('c4m2_esp_baja')} que esperan "
                f"menos de 5, casi todo ese índice cabe en el azar del conteo de un Poisson "
                f"homogéneo.", False,
                f"No cabe: el χ² que compara cada conteo con la esperanza de su propia celda da "
                f"{c('c4m2_chi2')} con {c('c4m2_gl')} grados de libertad. Con {c('c4m2_esp_baja')} "
                f"celdas que esperan menos de 5 la aproximación cojea, pero el margen es tal que la "
                f"conclusión no cambia.")]),

    preg("opcion", "cap4", 3,
         f"Con las sedes del perímetro urbano, el índice de Clark-Evans sin corregir, R, vale "
         f"{c('c4m3_ce_bog')}. Con las sedes del Distrito Capital y su ventana —"
         f"{c('c4m1_n_dc')} sedes en {c('c4m1_area_dc')}— baja a {cn('ce_ventana.ce_dc')}. "
         f"¿Qué explica la bajada?",
         "Mira qué cifras del enunciado dependen de la ventana.",
         opciones=[
             op("Al pasar a la ventana del D.C. cambia la referencia: R divide por la distancia que "
                "daría el azar con la λ de la ventana, y el suelo rural baja esa λ.", True,
                f"R es la distancia media de cada sede a su vecina más próxima dividida por la que "
                f"daría el azar, 1/(2√λ). Con el D.C. entran {cn('resto_dc.n_resto')} sedes rurales, "
                f"pero sobre todo entran {cn('resto_dc.area_resto_km2')} casi vacíos: la λ cae de "
                f"{c('c4m1_lambda_urb')} a {c('c4m1_lambda_dc')}, y la distancia del azar se alarga de "
                f"{c('c4m3_nn_esp_bog')} a {cn('ce_ventana.nn_esp_dc')}. La observada también sube, de "
                f"{c('c4m3_nn_bog')} a {cn('ce_ventana.nn_dc')}, pero mucho menos. Es el módulo 1 visto "
                f"desde el 3: la ventana es parte del estimador."),
             # Sin las cifras del resto del Distrito: con ellas, el A01 se
             # resolvía leyendo esta pregunta (forma, ronda 5).
             op("Al pasar a la ventana del D.C. entran las sedes rurales, más agrupadas que las "
                "urbanas, y arrastran hacia abajo la distancia media a la vecina.",
                False,
                f"Pasa lo contrario: las {cn('resto_dc.n_resto')} sedes rurales están aisladas, y la "
                f"distancia media observada sube de {c('c4m3_nn_bog')} a {cn('ce_ventana.nn_dc')}. Lo "
                f"que se dispara es la distancia que daría el azar con la λ de la ventana, de "
                f"{c('c4m3_nn_esp_bog')} a {cn('ce_ventana.nn_esp_dc')}."),
             op("Al pasar a la ventana del D.C. el índice compara sedes separadas por kilómetros, y "
                "a esa escala de kilómetros las sedes se agrupan más.", False,
                f"R no compara a ninguna escala elegida: usa solo la distancia de cada sede a su "
                f"vecina más próxima. Para las sedes urbanas esa distancia casi no cambia al pasar al "
                f"D.C.; la media sube porque entran las {cn('resto_dc.n_resto')} rurales, que están "
                f"aisladas. Lo que cambia sobre todo es la λ con que se calcula la referencia del azar, "
                f"y lo que el D.C. añade es suelo sin ciudad, que no es una propiedad del patrón."),
             op("Al pasar a la ventana del D.C. entra el suelo rural y crece el perímetro: sin "
                "corregir, el borde alcanza a más sedes y es él quien baja el índice.", False,
                "El borde empuja hacia el otro lado: a una sede de la orilla le faltan vecinas y se le "
                "mide una más lejana que la real, así que R sin corregir sale más alta, no más baja. La "
                "bajada viene del denominador: la distancia que daría el azar, que se alarga con la λ "
                "del D.C.")]),

    preg("multiple", "cap4", 4,
         f"El capítulo simuló {c('c4m4_n_real')} realizaciones de CSR con λ = {c('c4m4_lambda')} en "
         f"el cuadrado unidad: el índice de Clark-Evans sin corregir dio de media "
         f"{c('c4m4_R_media')}, y {c('c4m4_R_bajo1')} quedaron por debajo de 1. Se repite con "
         f"λ = {cn('denso.lambda')}, diez veces más puntos en el mismo cuadrado. Marca todo lo que "
         f"es cierto.",
         "Separa lo que podría cambiar con λ: el conteo de puntos y su varianza, el sesgo del índice "
         "y su temblor. ¿Qué cambia, y hacia dónde?",
         opciones=[
             op("La media del índice sin corregir baja hacia 1: con más densidad, a una fracción menor "
                "de los puntos se le escapa el vecino fuera de la ventana.", True,
                f"Baja a {cn('denso.R_media')}: el sesgo pasa de {cn('denso.sesgo_capitulo')} a "
                f"{cn('denso.sesgo')}. El vecino de verdad de un punto solo puede caer fuera si el "
                f"punto está más cerca del borde que de su vecino, y con más densidad esa franja se "
                f"estrecha. En número, los puntos de la franja son más —es más estrecha, pero con diez "
                f"veces más densidad—, y aun así pesan menos en la media, porque son una fracción "
                f"menor de todos. No desaparece: el estimador sin corregir sigue por encima de 1."),
             op(f"La proporción de realizaciones con un índice por debajo de 1, que en el capítulo era "
                f"el {cn('denso.pct_bajo1_capitulo')}, se queda cerca de esa cifra con "
                f"λ = {cn('denso.lambda')}.", True,
                f"Quedan {cn('denso.R_bajo1')} de {cn('denso.n_real')} por debajo de 1, el "
                f"{cn('denso.pct_bajo1')}, frente al {cn('denso.pct_bajo1_capitulo')} del capítulo. "
                f"El sesgo se encoge, pero el azar de R también —su desviación típica baja de "
                f"{c('c4m4_R_sd')} a {cn('denso.R_sd')}— y casi al mismo ritmo, el de 1/√λ: el sesgo, "
                f"porque la franja del borde se estrecha con la distancia al vecino; el temblor, "
                f"porque R promedia diez veces más distancias. Por eso un índice por "
                f"debajo de 1 sigue sin bastar para declarar agregación, con pocos puntos o con muchos."),
             op(f"La media del índice sin corregir se queda cerca de {c('c4m4_R_media')}: el sesgo lo "
                f"pone el estimador, y el estimador es el mismo.", False,
                f"Es del estimador, y aun así depende de la densidad: con λ = {cn('denso.lambda')} "
                f"la media baja a {cn('denso.R_media')}. El sesgo lo ponen los puntos cuyo vecino cae "
                f"fuera, y con más densidad son una fracción menor de todos los puntos."),
             # Un par que se contradice y no lleva clave: con la media sube/se
             # queda/baja, de cada par contradictorio una opción era siempre la
             # correcta (forma y redacción, ronda 5; H17). La lección de la que
             # salió, «son más en número pero una fracción menor», pasa a la
             # retro de la clave.
             op("La varianza del número de puntos se queda igual: el cuadrado es el mismo, y la "
                "varianza de un conteo la fija la ventana, no la densidad.", False,
                f"La ventana es la misma, pero la varianza de un conteo de Poisson es su media, λ por "
                f"el área, y crece con λ: de {c('c4m4_var')} con λ = {c('c4m4_lambda')} a "
                f"{cn('denso.n_var')} con λ = {cn('denso.lambda')}. Ni se queda ni se reduce."),
             op("La varianza del número de puntos se reduce, porque con más puntos el conteo se "
                "estabiliza alrededor de su media.", False,
                f"El conteo es Poisson: su varianza vale lo mismo que su media, y crece con ella. Con "
                f"λ = {c('c4m4_lambda')} el capítulo midió media {c('c4m4_media')} y varianza "
                f"{c('c4m4_var')}; con λ = {cn('denso.lambda')}, {cn('denso.n_media')} y "
                f"{cn('denso.n_var')}. Lo que se estabiliza es la proporción entre el conteo y su "
                f"media, no el conteo.")]),

    preg("opcion", "cap4", 5,
         f"Las plántulas de secuoya y su versión rebarajada dentro de cada celda de una rejilla "
         f"{ej(5)} dan el mismo χ², {c('c4m5_chi2')}, con {c('c4m5_gl')} grados de libertad. "
         f"Con una rejilla {ej(10)}, el original da {cn('rebarajado.chi2_10_orig')} y el "
         f"rebarajado, {cn('rebarajado.chi2_10_reb')}. ¿Qué enseña que, con la rejilla fina, los "
         f"dos χ² dejen de coincidir?",
         "Repasa cómo se construyó el rebarajado.",
         opciones=[
             op(f"Que la rejilla es la escala a la que el test mira: el rebarajado conserva los "
                f"conteos de cada celda {ej(5)}, no los de sus cuartos.", True,
                f"Dentro de cada celda {ej(5)} los puntos se repartieron al azar, así que cada "
                f"cuarto de celda recibe otro número. El χ² no ve lo que pasa por debajo de su "
                f"rejilla, y cambiar la rejilla cambia lo que ve. La distancia al vecino, que no "
                f"depende de ninguna rejilla, los distinguía desde el principio: el índice de "
                f"Clark-Evans sin corregir pasa de {c('c4m5_ce_orig')} a {c('c4m5_ce_reb')}."),
             op(f"Que, para el test, los dos son el mismo patrón: si solo se movieron plántulas dentro "
                f"de su celda {ej(5)}, la diferencia con la rejilla fina es ruido.", False,
                f"No es ruido: por debajo de la celda {ej(5)} el rebarajado borró los grumos, y la "
                f"rejilla fina mira justo a esa escala. Con la {ej(10)}, los dos χ², con los mismos "
                f"grados de libertad, valen {cn('rebarajado.chi2_10_orig')} y "
                f"{cn('rebarajado.chi2_10_reb')}: es la diferencia entre un patrón con grumos y otro "
                f"sin ellos."),
             op(f"Que dentro de cada celda {ej(5)} el rebarajado quedó más agregado que el original, y "
                f"el χ² fino lo detecta porque mira por debajo de esa celda.", False,
                f"Quedó menos agregado, no más: con la rejilla fina su χ² es menor, "
                f"{cn('rebarajado.chi2_10_reb')} frente a {cn('rebarajado.chi2_10_orig')}. Repartir al "
                f"azar las plántulas dentro de cada celda borra los grumos que había por debajo de ella."),
             op("Que, si cada celda espera al menos 5 plántulas, el χ² fino es el que hay que creer, "
                "porque tiene más grados de libertad.", False,
                f"La condición no se cumple: con la rejilla {ej(10)} cada celda espera "
                f"{c('c4m6_red_emin10')} plántulas, muy por debajo de 5, y el p-valor sale de una "
                f"aproximación que ya no vale. Y aun cumpliéndose, más grados de libertad no hacen más "
                f"creíble una escala que otra: cada rejilla contesta por su escala.")]),

    preg("grafico", "cap4", 6,
         f"El gráfico da, para cada rejilla del barrido, cuántas sedes espera la celda de menor "
         f"esperanza si λ fuera constante, en escala logarítmica. Las barras corresponden a la "
         f"ventana urbana; la línea, a las mismas {c('c4m1_n_urb')} sedes en un rectángulo de la "
         f"misma área, donde cada celda de una rejilla k × k espera n/k². La línea discontinua marca "
         f"5. ¿Qué separa las barras de la línea?",
         "Pregúntate qué entra en la esperanza de una celda y qué no.",
         alto=250,
         descripcionGrafico=(
             "Barras, una por rejilla, con la esperanza de la celda de menor esperanza en la "
             "ventana urbana: "
             + "; ".join(f"{ej(k)}, {sig2(e)}" for k, e in zip(NX, SUP["esperanza_min"]))
             + ". Línea, la misma cifra en un rectángulo de la misma área: "
             + "; ".join(f"{ej(k)}, {n(e, 2)}" for k, e in zip(NX, RECT))
             + ". Una línea discontinua horizontal marca 5."),
         dibujar="""canvas => {
            const g = DATOS_PRE2.graficos.g_supuesto;
            const ejes = ejesPreparcial('Rejilla de k × k celdas (k)', 'Sedes esperadas (escala log)',
                                        ejeLogPreparcial());
            // En el teléfono, a 11 px, «15» y «20» quedaban a 1.4 px y se leía
            // «1520» (gráficos, ronda 5).
            ejes.x.ticks = Object.assign({}, ejes.x.ticks, { autoSkip: false, maxTicksLimit: 20,
              font: ctx => ({ family: 'Montserrat', size: estrechoPreparcial(ctx) ? 9 : 11 }) });
            ejes.y.ticks = Object.assign({}, ejes.y.ticks,
              { font: ctx => ({ family: 'Fira Code', size: estrechoPreparcial(ctx) ? 10 : 11 }) });
            return crearGraficoLinea(canvas, g.nx.map(k => String(k)), [
              { type: 'bar', label: 'Ventana urbana', corto: 'Ventana', data: g.esperanza_min,
                backgroundColor: COLORES_GRAFICO.primario, borderWidth: 0, order: 3 },
              { label: 'Rectángulo de la misma área', corto: 'Rectángulo', data: g.rectangulo,
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent',
                pointRadius: 3, borderWidth: 2, order: 1 },
              { label: '5 sedes esperadas', corto: 'Línea del 5', data: g.nx.map(() => 5),
                borderColor: GRIS_REFERENCIA, backgroundColor: 'transparent',
                borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5, order: 2 }
            ], { scales: ejes,
                 plugins: pluginsPreparcial(null, { titulo: it => 'Rejilla ' + it.label + ' × ' + it.label }) });
          }""",
         opciones=[
             op("La forma de la ventana: en el rectángulo todas las celdas miden lo mismo, y en la "
                "ciudad las del borde se quedan con un pedazo.", True,
                f"La esperanza de una celda es λ por su área dentro de la ventana. Con las mismas "
                f"sedes y la misma área, el rectángulo da n/k² a cada celda, y su mínimo desciende en "
                f"escalera suave sin caer por debajo de 5 en todo el barrido: con la {ej(NX[-1])} aún "
                f"espera {n(RECT[-1], 2)}. La ciudad baja de 5 ya con la {ej(K_BAJA)}, con una celda que "
                f"espera {sig2(EMIN[K_BAJA])}, y con la {ej(10)} tiene una que espera "
                f"{sig2(EMIN[10])}. Por eso el supuesto se comprueba sobre la ventana de verdad, "
                f"rejilla por rejilla."),
             op("El agrupamiento de las sedes: en la ciudad se apiñan en unos barrios y dejan "
                "celdas casi vacías, cosa que en el rectángulo no pasaría.", False,
                "La esperanza no mira dónde están las sedes: es la que tendría cada celda si λ fuera "
                "constante. Las celdas casi vacías del dato son el conteo observado, que este gráfico "
                "no muestra."),
             op("El tamaño de las celdas: la rejilla se tiende sobre el rectángulo que encierra la "
                "ciudad, mayor que ella, y sus celdas esperan menos.", False,
                f"Es verdad que la rejilla se tiende sobre el rectángulo que encierra la ciudad, y "
                f"por eso cada celda entera es mayor que en un rectángulo de la misma área: espera más, "
                f"no menos. De media, cada celda viva espera {c('c4m2_media')} sedes con la {ej(10)}, "
                f"frente a {n(RECT_K[10], 2)} en el rectángulo. Lo que baja el mínimo es el pedazo que "
                f"les queda a las celdas del borde."),
             op("El área útil: la ciudad tiene huecos y cerros sin sedes, y por eso cada celda espera "
                "menos que en un rectángulo de la misma área.", False,
                f"El rectángulo de la línea tiene la misma área y las mismas sedes, así que la misma "
                f"λ, y una celda espera λ por su área sin mirar si en ella hay sedes. Lo que baja el "
                f"mínimo no es el área total, sino cómo cortan la ventana las líneas de la rejilla.")]),

    preg("multiple", "cap4", 7,
         f"Los pinos suecos (<code>swedishpines</code>, {cn('gf_suecos.n')} árboles en un "
         f"rectángulo de {cn('gf_suecos.lado_x_m')} × {cn('gf_suecos.lado_y_m')}) se leen con las "
         f"tres medianas del módulo 7: la mitad de los árboles tiene su vecino más próximo a menos "
         f"de {cn('gf_suecos.g_mediana_m')}; la F, corregida por el borde con muestra reducida, "
         f"llega a la mitad en {cn('gf_suecos.f_mediana_m')}; y bajo CSR, con la misma intensidad, "
         f"las dos medianas valdrían {cn('gf_suecos.csr_mediana_m')}. Marca todo lo que es cierto.",
         "G mira desde los árboles y F desde cualquier sitio de la ventana: piensa qué dice que "
         "cada una llegue a la mitad antes o después que la del azar.",
         opciones=[
             op("G llega tarde y F pronto: los árboles tienen su vecino más lejos de lo que pondría el "
                "azar y dejan menos huecos. Las dos apuntan a la regularidad.", True,
                f"La mediana de G, {cn('gf_suecos.g_mediana_m')}, pasa de la del azar, "
                f"{cn('gf_suecos.csr_mediana_m')}: los vecinos están más lejos. La de F, "
                f"{cn('gf_suecos.f_mediana_m')}, queda por debajo: desde casi cualquier sitio hay un "
                f"árbol cerca. Un patrón regular hace las dos cosas a la vez, como las células del "
                f"capítulo; uno agregado haría lo contrario en las dos."),
             op(f"Ninguna de las tres cifras dice si el apartamiento supera al que produce el azar con "
                f"{cn('gf_suecos.n')} árboles: para eso hay que compararlas con simulaciones, como hace "
                f"una envolvente.", True,
                "Una mediana es una cifra de una sola realización, y con tan pocos árboles tiembla. "
                "Saber si se aparta del azar más de lo que el azar se aparta de sí mismo es el módulo "
                "11. Lo que sí dicen las tres cifras es la dirección."),
             op("G llega tarde y F pronto: los árboles tardan en encontrar vecino porque se apiñan en "
                "unos pocos grupos y dejan el resto de la ventana vacío.", False,
                "En un patrón agregado pasa al revés en las dos: el vecino está cerca, dentro del "
                "grupo, y G llega pronto; y entre grupos quedan huecos grandes, así que F llega tarde. "
                "Es lo que el capítulo mide en las secuoyas."),
             # Una abstención falsa que hace juego con la verdadera (la de la
             # envolvente): antes la única que se abstenía era clave (forma,
             # ronda 5).
             op("Se contradicen —G dice que los árboles están lejos unos de otros, y F, que están cerca "
                "de todo—, así que sin una envolvente no se sabe hacia qué lado se aparta el patrón.",
                False,
                "No se contradicen: miran desde sitios distintos. Un patrón regular deja cada árbol "
                "lejos de los demás y, a la vez, reparte los árboles tan parejo que ningún sitio queda "
                "lejos de uno. Por eso se leen juntas, y juntas dicen la dirección: hacia la "
                "regularidad. Lo que no dicen sin simular es si el apartamiento supera al azar."),
             # Antes era la negación literal de la clave de la envolvente («con
             # eso basta sin simular»), y de cada par contradictorio una era
             # clave (H17, ronda 5). Ahora falla por el sentido de J.
             op(f"La J de los pinos, (1 − G)/(1 − F), queda por debajo de 1 en el tramo en que se lee, "
                f"mientras F no pasa de {c('c4m7_umbral_f')}, como corresponde a un patrón regular.",
                False,
                f"Al revés en las dos cosas. En un patrón regular G crece más despacio que F, así que "
                f"1 − G pasa de 1 − F y J pasa de 1; y la de los pinos queda por encima de 1 en las "
                f"{cn('gf_suecos.j_nodos')} distancias en que se dibuja, las que dejan F por debajo de "
                f"{c('c4m7_umbral_f')}. Aun así, pasar de 1 no basta para declarar regularidad sin "
                f"simular: J tiembla igual que G y F, y más cerca del tope de F, donde su denominador "
                f"es un resto pequeño.")],
         giro=3),

    preg("multiple", "cap4", 8,
         "Sobre lo que la función K puede y no puede decir, marca todo lo que es cierto.",
         "Recuerda qué guarda K de cada pareja de puntos, y hasta dónde puede mirar.",
         opciones=[
             op(f"Sigue diciendo algo a distancias en que G ya vale 1: en las sedes, G se agota a "
                f"{c('c4m8_vecino_max')}, y el barrido de K llega hasta {c('c4m8_rmax')}.", True,
                "G solo usa la distancia de cada punto a su vecino más próximo, y pasada la mayor "
                "de ellas vale 1 y ya no cuenta nada. K usa todas las parejas hasta r."),
             op(f"Multiplicada por λ, se lee en vecinas por punto: en las sedes, unas "
                f"{c('c4m8_vecinas')} a 1&nbsp;km o menos de cada sede, frente a las "
                f"{c('c4m8_vecinas_csr')} que daría el azar.", True,
                "λK(r) es el número esperado de vecinas a distancia r o menos de un punto típico. "
                "Dividir por λ deja una curva cuya referencia bajo CSR, πr², no depende de la "
                "densidad; multiplicar por ella devuelve la cuenta de vecinas, que es lo que se "
                "entiende."),
             op("Si la K estimada coincide con πr² a lo largo del barrido, el proceso que la generó es "
                "un Poisson homogéneo.", False,
                "Baddeley y Silverman construyeron un proceso que no es de Poisson y cuya K es "
                "exactamente πr². Una K pegada a πr² es compatible con CSR, no la prueba."),
             op(f"Distingue un patrón alineado a lo largo de una avenida de uno en grumos redondos: a "
                f"1&nbsp;km, cada una de las {c('c4m8_parejas')} parejas de sedes entra con su "
                f"dirección.", False,
                "K solo mira distancias: una alineación sube K como cualquier grumo, pero su "
                "dirección se promedia con todas las demás y no se distingue de un grupo redondo. "
                "Es el supuesto de isotropía."),
             # Antes falsa, y las tres falsas eran las tres absolutas; además la
             # clave era la más corta (forma, ronda 5). Ahora es una tercera
             # clave, y sin precipicio: pasado el alcance los pesos no se
             # disparan (1.68 de media justo antes, 1.79 justo después) ni la
             # varianza de K salta; la regla de Ripley es práctica, no un
             # umbral de validez (verdad, ronda 5).
             op(f"Por defecto, <code>Kest</code> se detiene en {c('c4m8_rmax')}, un cuarto del lado "
                f"corto del rectángulo que encierra la ventana urbana, porque cuanto más larga es una "
                f"pareja, más la tienen que pesar la isotrópica y la de traslación.", True,
                f"Es la regla práctica de Ripley, la que <code>Kest</code> aplica por defecto, y el "
                f"capítulo no la pasa. Cuanto más larga es una pareja, menos probable es que quepa "
                f"entera en la ciudad, y más pesa la que sí se observó. Con la corrección de "
                f"traslación, el peso medio de las parejas a 1&nbsp;km o menos es "
                f"{c('c4m8_peso_1km')}; en la última décima antes de {c('c4m8_rmax')}, "
                f"{c('c4m8_peso_rmax')}; y en la última décima antes del doble de esa distancia, "
                f"{c('c4m8_peso_doble')}, con alguna pareja contada por {c('c4m8_peso_doble_max')}. "
                f"No es un precipicio: pasado ese radio la curva no se rompe de golpe, pero la "
                f"sostienen pesos cada vez más grandes. Para mirar más lejos se le pasa "
                f"<code>r</code> a <code>Kest</code>, y se declara.")]),

    preg("grafico", "cap4", 9,
         "El gráfico es la correlación de pares g(r) de las sedes en la ventana urbana; la línea "
         "de puntos marca 1, lo que daría CSR. Lee la curva a unos 3&nbsp;km. ¿Qué afirma ese "
         "valor?",
         "Recuerda cómo se obtiene g a partir de K.",
         alto=250,
         descripcionGrafico=(
             f"Curva de g(r) de las sedes, de {ent(R1_PCF)}&nbsp;m a {c('c4m9_r_final')}. Arranca "
             f"en {c('c4m9_g_max')}. Valores en algunos radios: "
             + "; ".join(f"{ent(PCF['r'][i])}&nbsp;m, {n(PCF['g'][i], 3)}" for i in NODOS_PCF)
             + f"; en el último, {c('c4m9_g_final')}. La línea de puntos marca 1."),
         dibujar="""canvas => {
            const g = DATOS_PRE2.graficos.g_pcf;
            const i0 = g.r.findIndex(r => r > 0);
            const r = g.r.slice(i0), v = g.g.slice(i0);
            return crearGraficoLinea(canvas, [], [
              { label: 'g(r) de las sedes', corto: 'g(r)', data: puntosXY(r, v), borderColor: COLORES_GRAFICO.primario,
                backgroundColor: 'transparent', pointRadius: 0, borderWidth: 2, tension: 0.2 },
              { label: 'CSR', data: puntosXY(r, r.map(() => 1)), borderColor: GRIS_REFERENCIA,
                backgroundColor: 'transparent', borderDash: [2, 3], pointRadius: 0, borderWidth: 1.5 }
            ], { scales: { x: ejeKmPreparcial(r), y: ejesPreparcial('', 'g(r)', { min: 0.9 }).y },
                 plugins: pluginsPreparcial(null, { tituloRadio: true }) });
          }""",
         opciones=[
             op(f"Que en un anillo estrecho a unos 3&nbsp;km de una sede hay un {n(LEC['pct'], 0)}&nbsp;% "
                f"más de sedes por unidad de área que si estuvieran al azar con la misma intensidad media.",
                True,
                f"g compara la densidad de sedes en el anillo de radio r alrededor de una sede con la "
                f"intensidad media: a {ent(LEC['r'])}&nbsp;m vale {n(LEC['g'], 4)}, un "
                f"{n(LEC['pct'], 1)}&nbsp;% más. Es una afirmación sobre ese anillo y nada más. Por "
                f"qué hay más —sedes que se atraen o una λ que cambia de un barrio a otro— no lo dice, "
                f"y eso es el capítulo 5."),
             op(f"Que, contando todas las sedes a 3&nbsp;km o menos de cada una, sale un "
                f"{n(LEC['pct'], 0)}&nbsp;% más de las que pondría el azar con la intensidad de la "
                f"ciudad.", False,
                f"Eso lo diría K(r)/πr², que mira el disco entero y acumula el exceso de todas las "
                f"distancias cortas: a ese radio vale {n(LEC['disco'], 2)}, no {n(LEC['g'], 2)}. g "
                f"mira solo el anillo, y por eso puede bajar mientras K(r)/πr² sigue alto."),
             op(f"Que el {n(LEC['pct'], 0)}&nbsp;% de las sedes tiene su vecina más próxima a unos "
                f"3&nbsp;km, y las demás la tienen más cerca o más lejos.", False,
                f"Eso sería una lectura de G, que cuenta sedes por la distancia a su vecina más "
                f"próxima. g no cuenta sedes, compara densidades; y en las sedes ninguna tiene su "
                f"vecina más próxima a más de {c('c4m8_vecino_max')}."),
             op(f"Que cada sede tiene, de media, {n(LEC['g'], 2)} vecinas a unos 3&nbsp;km, frente a la "
                f"única que pondría el azar a esa distancia.", False,
                "g no cuenta vecinas: es un cociente entre dos densidades, sin unidades. Para pasar a "
                "vecinas hace falta multiplicar por λ y por el área del anillo, que depende de su "
                "ancho.")]),

    preg("multiple", "cap4", 10,
         f"La corrección de traslación da a cada pareja de puntos el peso |W| / |W ∩ (W + v)|, "
         f"donde v es el vector que va de un punto al otro y W + v es la ventana desplazada por v. "
         f"Desplazada {cn('traslacion.d_corta_m')} hacia el este, la ventana urbana conserva el "
         f"{cn('traslacion.frac_este_100')} de su área. Marca todo lo que es cierto.",
         "Lee la fórmula término a término y pregúntate de qué depende cada uno.",
         opciones=[
             op("Dos parejas con el mismo vector pesan lo mismo, aunque una esté en pleno centro y "
                "la otra pegada al borde.", True,
                "La fórmula no mira dónde está la pareja: solo cuánto se solapa la ventana con su "
                "copia desplazada. Es una corrección de la forma de la ventana, no de la posición de "
                "los puntos; la isotrópica, en cambio, sí mira dónde está cada punto."),
             op(f"Con la traslación ninguna pareja de sedes separadas pesa exactamente 1: dos sedes a "
                f"{cn('traslacion.d_corta_m')} una de otra en dirección este pesan "
                f"{cn('traslacion.peso_este_100')}.", True,
                f"Es el inverso de lo que se conserva, el {cn('traslacion.frac_este_100')}. Para "
                f"cualquier vector que no sea nulo la ventana desplazada pierde algo: lo que el peso "
                f"compensa es la probabilidad de que una pareja con ese vector cayera entera dentro. "
                f"Solo las parejas de sedes que comparten coordenadas —{c('c5m11_repetidas')} sedes "
                f"repiten las de otra— tienen v nulo, y esas pesan 1."),
             op(f"Dos sedes a {cn('traslacion.d_corta_m')} en pleno centro pesan 1 con la isotrópica y "
                f"con la de traslación, aunque la ventana desplazada pierda algo lejos de ellas.", False,
                f"Con la isotrópica sí, si el círculo de ese radio alrededor de la sede cabe entero en "
                f"la ciudad. Con la de traslación, no: pesa más de 1 —"
                f"{cn('traslacion.peso_este_100')} si la pareja va de este a oeste, "
                f"{cn('traslacion.peso_norte_100')} si va de norte a sur—, porque depende de la ventana "
                f"entera y no del sitio de la pareja."),
             op("Las parejas este-oeste y las norte-sur separadas lo mismo pesan igual, porque la "
                "corrección solo mira la distancia entre los dos puntos.", False,
                f"Mira el vector entero, dirección incluida: hacia el este la ventana conserva el "
                f"{cn('traslacion.frac_este_100')} y hacia el norte el "
                f"{cn('traslacion.frac_norte_100')}. La que no mira la dirección es la isotrópica."),
             # Contraria a la de «pesan igual», y falsa como ella: un par que se
             # contradice sin clave (H17, ronda 5). La lección de la distancia,
             # que era la de esta opción, sigue en su retro.
             op(f"Dos sedes separadas {cn('traslacion.d_corta_m')} de norte a sur pesan más que dos "
                f"separadas lo mismo de este a oeste, porque la ciudad es más larga de norte a sur.",
                False,
                f"Al revés. Desplazada hacia el norte, la ventana pierde una franja a lo ancho de la "
                f"ciudad, y hacia el este, una a lo largo: si la ciudad es más larga de norte a sur, la "
                f"pareja norte-sur es la que pesa menos, {cn('traslacion.peso_norte_100')} frente a "
                f"{cn('traslacion.peso_este_100')}. La diferencia es pequeña porque el contorno, muy "
                f"quebrado, pierde área en cualquier dirección. Lo que sí hace crecer el peso es la distancia: a {cn('traslacion.d_larga_m')} hacia "
                f"el este, {cn('traslacion.peso_este_1000')}, porque las parejas largas son las que "
                f"tenían menos probabilidad de caer enteras dentro.")]),

    preg("numerica", "cap4", 11,
         f"Vas a construir una envolvente con nsim = {cn('nrank.nsim')} simulaciones. ¿Qué rango "
         f"—el argumento <code>nrank</code>— tienes que pedir para que la banda sea un contraste "
         f"puntual al {cn('nrank.nivel_pct')}? Da un número entero.",
         "Repasa qué nivel puntual tiene una banda de rango k.",
         respuesta=val_nuevo("nrank.correcto"), tolerancia=0,
         retroAcierto=(
             f"Con rango k, el nivel puntual de la banda es 2k/(nsim + 1): con k = "
             f"{cn('nrank.correcto')} y {cn('nrank.nsim')} simulaciones sale el "
             f"{cn('nrank.nivel_pct')}. Con el rango por defecto, k = 1, la banda sería un contraste "
             f"puntual al {cn('nrank.nivel_defecto_pct')}. El test global es otra cosa: con "
             f"{cn('nrank.nsim')} simulaciones, el p-valor más pequeño que puede dar es 1/(nsim + 1) = "
             f"{cn('nrank.p_minimo')}; con las {c('c4m11_nsim')} del capítulo, "
             f"{c('c4m11_p_min')}."),
         retroFallo=(
             f"La regla: el nivel puntual es 2k/(nsim + 1); iguálalo a {cn('nrank.nivel')} y despeja "
             f"k. Si respondiste {dist('nrank', 'una_cola')}, olvidaste que la banda tiene dos lados; "
             f"si respondiste {dist('nrank', 'defecto')}, te quedaste con el rango por defecto, que "
             f"con {cn('nrank.nsim')} simulaciones da un contraste al "
             f"{cn('nrank.nivel_defecto_pct')}.")),
]


# ---------------------------------------------------------------------
# BLOQUE B · capítulo 5
# ---------------------------------------------------------------------
# El texto alternativo del 5.10 da valores, no la lectura: la observada y el
# borde alto de la banda en unos pocos radios, elegidos por cercanía a cada
# kilómetro y en los dos extremos del tramo que se sale. Selección de nodos.
_KR = KIN["r"]
NODOS_KIN = sorted({0} | {min(range(len(_KR)), key=lambda i, d=d: abs(_KR[i] - d))
                          for d in (1000, 2000, 3000, val("c5m10_ultimo"), 5000)} | {len(_KR) - 1})

BLOQUE_B = [
    preg("opcion", "cap5", 1,
         f"Estimas la intensidad de las {c('c5m1_n_ken')} sedes de Kennedy, una localidad de "
         f"{c('c5m1_area_ken')}, por núcleos y con la corrección de borde por defecto, y vas abriendo "
         f"σ hasta que el núcleo es mucho más ancho que la localidad. ¿A qué tiende la superficie?",
         # La pista ya no copia la clave («una vecindad que lo abarca todo»), y
         # la cifra de la clave aparece también en un distractor: era la única
         # comprobable y estaba sola en la correcta (forma, ronda 5).
         "Piensa en cuánto pesa una sede lejana frente a una cercana cuando el núcleo es casi "
         "plano, y en qué hace la corrección de borde con la masa que se sale.",
         opciones=[
             op(f"A una constante: la λ = n/|W| del capítulo 4, {c('c5m1_lambda_ken')} en cada sitio "
                f"de la localidad, sin importar dónde estén las sedes.", True,
                f"Con σ muy grande cada núcleo es casi plano sobre la ventana, y la corrección divide "
                f"por la fracción que cae dentro, así que en cada sitio queda n/|W|: con un σ enorme, "
                f"la superficie va de {cn('limite.corregida_min_km2')} a "
                f"{cn('limite.corregida_max_km2')} en toda la localidad. La KDE es contar con una "
                f"vecindad que se solapa; con una vecindad del tamaño de la ventana, se cuenta todo y "
                f"se divide por toda el área. Por eso <code>bw.ppl</code>, ante un patrón sin "
                f"estructura, puede irse al σ más grande que le dejan probar (módulo 3)."),
             op("A cero en todas partes: cada sede se reparte sobre un área cada vez mayor, y la "
                "intensidad de cada sitio se diluye sin límite.", False,
                "Sin corregir el borde, la superficie sí baja: la masa de cada núcleo se sale de la "
                "ventana y se pierde. Con la corrección, la fracción del núcleo que queda dentro encoge "
                "al mismo ritmo que el núcleo se aplana, y el cociente se queda en n/|W|."),
             op("A un solo pico sobre el centro de masa de las sedes, porque es ahí donde se solapan "
                "a la vez todos los núcleos.", False,
                # El «pico único con anchos intermedios» era el de la superficie
                # sin corregir; con la corrección por defecto, que fija el
                # enunciado, el máximo se va al borde (verdad, ronda 5).
                "Eso le pasa a la superficie sin corregir: la suma de núcleos anchos es un bulto "
                "centrado cerca del centro de masa de las sedes. La corrección por defecto divide en "
                "cada sitio por la fracción del núcleo que cae dentro, que es más pequeña junto al "
                "borde, y deshace ese bulto: al abrir σ, el máximo corregido se va hacia el borde de "
                "la localidad, y con σ enorme ya no queda pico en ninguna parte, solo n/|W|."),
             op(f"Al mapa de cuadrantes: con σ grande cada vecindad se vuelve una celda de bordes "
                f"rectos, y la superficie se escalona alrededor de {c('c5m1_lambda_ken')}.", False,
                "El nivel es ese, pero la superficie no se escalona. Un mapa de cuadrantes da un valor "
                "por celda y salta de una a otra; un σ que crece sin límite deja la superficie sin "
                "ninguna variación, ni saltos ni escalones.")]),

    preg("grafico", "cap5", 2,
         "El gráfico da la intensidad máxima de la superficie de Kennedy para cada uno de los "
         "siete anchos de banda del módulo 2, con el mismo núcleo. Un informe publica los siete "
         "mapas, cada uno con su escala de color de cero a su propio máximo, y concluye: «el ancho "
         "de banda no cambia cuánta intensidad hay, solo el tamaño de las manchas». Con el gráfico "
         "delante, ¿qué le contestas?",
         "Compara lo que dice la curva con lo que vería quien solo mira los siete mapas.",
         alto=240,
         descripcionGrafico=(
             f"Curva de la intensidad máxima, en sedes por km², contra el ancho de banda, en "
             f"metros, para los siete anchos: "
             + "; ".join(f"σ = {ent(s)}&nbsp;m, {n(m, 2)}" for s, m in zip(PICO["sigma"], PICO["maximo"]))
             + "."),
         dibujar="""canvas => {
            const g = DATOS_PRE2.graficos.g_pico;
            // El título largo medía 219 px en un lienzo de 206 y Chart.js lo
            // aplastaba; en el teléfono va uno corto (gráficos, ronda 5).
            const ejes = ejesPreparcial('', 'Sedes por km²', { beginAtZero: true });
            ejes.x.title.text = ctx => estrechoPreparcial(ctx) ? 'σ en metros (× √2 cada paso)'
                                                               : 'σ (metros; cada uno √2 veces el anterior)';
            return crearGraficoLinea(canvas, g.sigma.map(s => milesPreparcial(s)), [
              { label: 'Intensidad máxima (sedes por km²)', corto: 'Pico', data: g.maximo,
                borderColor: COLORES_GRAFICO.primario, backgroundColor: 'transparent',
                pointRadius: 3, borderWidth: 2, tension: 0.2 }
            ], { scales: ejes, plugins: pluginsPreparcial(null, { sinLeyenda: true,
                                                                  titulo: it => 'σ = ' + it.label + ' m' }) });
          }""",
         opciones=[
             op(f"Que la conclusión la fabricó la escala: con una por mapa, cada uno llega al color más "
                f"oscuro en su pico, y el pico cae un {c('c5m2_caida')}.", True,
                f"La curva lo enseña: de {n(PICO['maximo'][0], 1)} a {n(PICO['maximo'][-1], 1)} sedes "
                f"por km². Con una escala por mapa esa caída no se ve: el lector ve siete mapas igual "
                f"de intensos, con manchas más o menos grandes, y el mapa contradice a la curva. Por "
                f"eso el capítulo pinta las siete superficies con una sola escala."),
             op("Que tiene razón en lo principal: el pico apenas cambia con el ancho, y una escala por "
                "mapa solo resalta los focos de cada superficie.", False,
                f"La curva dice lo contrario: el pico cae un {c('c5m2_caida')} entre los anchos "
                f"extremos, mucho más que el {c('c5m2_nucleo_dif')} que mueve cambiar de núcleo con el "
                f"mismo σ."),
             op("Que tiene razón, porque con la corrección de borde las siete superficies integran casi "
                "lo mismo, y con la misma masa la intensidad es la misma.", False,
                "La misma masa repartida sobre más área da un pico más bajo, y es justo por eso que el "
                "pico cae al abrir σ. Que las siete integren casi lo mismo es lo que hace honesta una "
                "escala común, no lo que la hace innecesaria."),
             op("Que se equivoca de causa: lo que cambia la intensidad es el núcleo, y con el mismo "
                "núcleo los siete mapas sí son igual de intensos.", False,
                f"El núcleo mueve el pico un {c('c5m2_nucleo_dif')} con el mismo σ; el ancho, un "
                f"{c('c5m2_caida')}. Con el mismo núcleo y siete anchos, los mapas no son igual de "
                f"intensos: lo parecen solo con una escala por mapa.")]),

    preg("numerica", "cap5", 3,
         f"<code>bw.ppl</code> busca el ancho de banda dentro de un intervalo, y si su criterio sigue "
         f"mejorando hasta el extremo, devuelve el extremo. Sobre un patrón en una ventana "
         f"rectangular de {cn('tope_ppl.lado_x_m')} × {cn('tope_ppl.lado_y_m')}&nbsp;m, ¿qué valor "
         f"delataría que chocó con el tope de su intervalo? En metros; se acepta una diferencia de "
         f"{ent(1)}.",
         "El tope lo pone la ventana, no el patrón: recuerda de qué medida de la ventana sale.",
         respuesta=val_nuevo("tope_ppl.correcto"), tolerancia=1, unidad="m",
         retroAcierto=(
             f"El tope es la mitad del diámetro de la ventana —la mayor distancia entre dos de sus "
             f"puntos—, y en un rectángulo el diámetro es la diagonal: {cn('tope_ppl.correcto')}. Y "
             f"no es un caso raro: sobre {cn('tope_ppl.csr_realizaciones')} patrones de CSR de unos "
             f"{cn('tope_ppl.csr_puntos_esperados')} puntos en ese rectángulo, <code>bw.ppl</code> "
             f"devolvió exactamente ese tope en {cn('tope_ppl.csr_chocan_en_el_tope')}. Para un patrón "
             f"sin estructura la mejor intensidad es una constante, que es un σ infinito: en esos "
             f"{cn('tope_ppl.csr_chocan_en_el_tope')}, el criterio siguió mejorando hasta el extremo. "
             f"En los otros {cn('tope_ppl.csr_no_chocan')}, el azar del patrón le dio un óptimo "
             f"finito, de {cn('tope_ppl.csr_sigma_min_m')} a {cn('tope_ppl.csr_sigma_max_m')}, que "
             f"sobre un patrón sin estructura tampoco describe nada. El tope no es un óptimo sino el extremo "
             f"del intervalo —la «pared» del capítulo—, y la única forma de notarlo es comparar lo "
             f"que devuelve con ese extremo."),
         retroFallo=(
             f"El tope es la mitad del diámetro, y el diámetro de un rectángulo es su diagonal. Los "
             f"valores {dist('tope_ppl', 'mitad_lado_mayor')} y {dist('tope_ppl', 'mitad_lado_menor')} "
             f"son mitades de los lados; {dist('tope_ppl', 'diagonal_entera')} es la diagonal "
             f"entera.")),

    preg("opcion", "cap5", 4,
         f"Estimas la intensidad de las {c('c5m4_n')} sedes de Kennedy con σ = "
         f"{c('c5m4_sigma_800')} e integras la superficie sobre la ventana: te da "
         f"{c('c5m4_masa_def')}. ¿Qué corrección de borde usaste?",
         "Compara el resultado con el número de sedes, y piensa hacia qué lado puede equivocarse "
         "cada corrección.",
         opciones=[
             op("La de density.ppp por defecto, que divide la estimación de cada sitio por la fracción "
                "del núcleo que cae dentro, y con estas sedes pone masa de más.", True,
                f"Con estas sedes se pasa un {c('c5m4_exceso')}. No es una ley del método: esa "
                f"corrección divide la estimación de cada sitio del mapa por la fracción del núcleo "
                f"centrado en ese sitio que cae dentro, y el total sale por encima o por debajo de n según a qué "
                f"distancia del borde caigan los puntos. La única que integra n siempre es la de "
                f"Diggle."),
             op("La superficie sin corregir, que con estas sedes cuenta dos veces la masa de los "
                "núcleos del borde y por eso se pasa.", False,
                f"Sin corregir pasa lo contrario: la masa de cada núcleo que se sale de la ventana "
                f"se pierde, y la integral se queda corta, en {c('c5m4_masa_sin')}."),
             op("La de diggle = TRUE, que con estas sedes corrige más fuerte que las otras dos y deja "
                "la integral por encima de n.", False,
                f"Esa es la que conserva el conteo: divide el núcleo de cada sede por la fracción de "
                f"ese núcleo que cae dentro, así que cada sede aporta exactamente 1 y la superficie "
                f"integra {c('c5m4_masa_dig')} a cualquier ancho."),
             op("Las tres dan casi lo mismo con estas sedes: la integral se aparta de n por la "
                "discretización de la rejilla del mapa, no por la corrección.", False,
                f"La rejilla mueve la integral muy poco; con diggle = TRUE da "
                f"{c('c5m4_masa_dig')}. Un exceso del {c('c5m4_exceso')} no es de la rejilla: es "
                f"de la corrección.")]),

    preg("multiple", "cap5", 5,
         f"El módulo 5 pinta tres capas sobre la ciudad con el mismo σ: la de oferta, con todas las "
         f"sedes ({c('c5m5_n_of')}); la de bachillerato, con las que tienen grado 11 "
         f"({c('c5m5_n_11')}); y la de evaluados, con esas mismas pesadas por su número de "
         f"evaluados de Saber 11. Marca todo lo que es cierto.",
         "Pregúntate qué cuenta cada capa: sedes o personas.",
         opciones=[
             op("La de evaluados ya no se mide en sedes por kilómetro cuadrado, sino en evaluados "
                "por kilómetro cuadrado.", True,
                f"Con diggle = TRUE, la corrección que usa el módulo, la KDE pesada integra la suma "
                f"de los pesos y no el número de puntos: sobre la ciudad devuelve los "
                f"{c('c5m5_total_est')} evaluados. Integra personas, así que su intensidad se mide en "
                f"evaluados por km², y eso es lo que la distingue de las otras dos."),
             op(f"La pareja que menos se parece es la de oferta contra evaluados, que correlacionan "
                f"{c('c5m5_cor_of_es')}, por debajo de las otras dos parejas.", True,
                f"Una capa cuenta sedes y la otra, estudiantes: donde las manchas no coinciden, "
                f"contar sedes deja de aproximar bien cuántos estudiantes hay. Las otras dos parejas "
                f"correlacionan {c('c5m5_cor_of_11')} (oferta y bachillerato) y {c('c5m5_cor_11_es')} "
                f"(bachillerato y evaluados). Ni una correlación de 1 las haría intercambiables —una "
                f"cuenta sedes y la otra, personas—; con {c('c5m5_cor_of_es')}, ni siquiera las "
                f"manchas caen del todo en los mismos sitios."),
             # Antes contradecía a la de la unidad en la superficie («integra
             # las mismas sedes» frente a «evaluados por km²»), y de cada par
             # contradictorio una era la clave (forma, ronda 5).
             op(f"La de evaluados pinta lo mismo que la de bachillerato: usa las mismas "
                f"{c('c5m5_n_11')} sedes y el mismo σ, y los pesos solo cambian la escala de color.",
                False,
                f"No pinta lo mismo: con la de bachillerato correlaciona {c('c5m5_cor_11_es')}, porque "
                f"una sede con muchos evaluados pesa más que una con pocos y mueve las manchas. Y no "
                f"integra {c('c5m5_n_11')} sedes sino {c('c5m5_total_est')} evaluados: los pesos "
                f"cambian lo que se cuenta, y con ello la unidad."),
             # «Pintan casi lo mismo» era cierto, y con cada mapa en su propia
             # escala también lo era «sirve de mapa de la otra» (revisión de
             # las múltiples, 2026-10-06): la falsedad va ahora en la escala.
             op(f"La de bachillerato y la de oferta correlacionan {c('c5m5_cor_of_11')}: con la "
                f"misma escala de color, el mapa de una serviría de mapa de la otra.", False,
                f"La correlación no mira la escala, solo dónde suben y bajan las dos superficies. La "
                f"de bachillerato cuenta el {c('c5m5_pct_11')} de las sedes —una sede de primaria no "
                f"tiene undécimo—, así que con la misma escala sale mucho más pálida: se parecen en "
                f"dónde están las manchas, no en cuánto valen. Publicar una por la otra cambia la "
                f"pregunta que contesta el mapa sin que cambie el título."),
             op("La de evaluados dice dónde viven los estudiantes que necesitarían colegio cerca de "
                "casa.", False,
                "Un estudiante cuenta donde estudia, no donde vive: la capa dice dónde estudian los "
                "que presentaron Saber 11, que no es lo mismo que dónde haría falta un colegio.")]),

    preg("numerica", "cap5", 6,
         f"En <code>chorley</code> —{c('c5m6_ch_casos')} cánceres de laringe, los casos, y "
         f"{c('c5m6_ch_controles')} de pulmón, los controles—, en el máximo del mapa de la "
         f"probabilidad de laringe la probabilidad de que un cáncer registrado sea de laringe es "
         f"{c('c5m6_ch_pmax')}. ¿Cuánto vale ahí el riesgo relativo, el cociente entre la intensidad "
         f"de los casos y la de los controles? Con dos decimales; se acepta una diferencia de "
         f"{n(0.01, 2)}.",
         "La probabilidad de caso y el riesgo relativo llevan la misma información en escalas "
         "distintas.",
         respuesta=float(n(val_nuevo("riesgo_relativo.correcto"), 2)), tolerancia=0.01,
         retroAcierto=(
             f"Si p = λ₁/(λ₁ + λ₀), el riesgo relativo r = λ₁/λ₀ es p/(1 − p): "
             f"{cn('riesgo_relativo.correcto')}. La probabilidad vive entre 0 y 1 y el riesgo "
             f"relativo entre 0 e infinito; <code>relrisk</code> devuelve la primera salvo que se le "
             f"pida <code>relative = TRUE</code>. Los dos cánceres tienen al tabaco detrás, y así lo "
             f"que el tabaco tiene de geográfico se cancela en el cociente."),
         retroFallo=(
             f"Si respondiste {dist('riesgo_relativo', 'contra_global')}, dividiste por la "
             f"proporción global, {c('c5m6_ch_global')}: eso dice cuántas veces la proporción local "
             f"supera a la de la comarca, que es otra pregunta. Si respondiste "
             f"{dist('riesgo_relativo', 'al_reves')}, el cociente está al revés. La relación es "
             f"r = p/(1 − p).")),

    preg("opcion", "cap5", 7,
         f"<code>rhohat</code> estima la intensidad de los {c('c5m7_bei_n')} árboles de "
         f"Beilschmiedia en función de la elevación del terreno. Alguien propone usar como "
         f"covariable «el número de árboles vecinos a 20 m o menos de cada sitio». ¿Qué le "
         f"contestas?",
         "Recuerda qué condición pide el capítulo a una covariable para que <code>rhohat</code> "
         "diga algo del proceso.",
         opciones=[
             op("Que esa covariable la fabrican los mismos árboles cuya intensidad se quiere explicar: "
                "la relación está garantizada antes de mirar.", True,
                "La elevación sirve porque se midió aparte de los árboles: la pregunta «¿hay más "
                "árboles donde el terreno es así?» se puede contestar con datos. Con una covariable "
                "hecha de los mismos árboles, la curva sube donde hay árboles por construcción, y no "
                "dice nada del terreno."),
             op("Que es mejor que la elevación, porque explica mucha más variación de la intensidad "
                "que los rasgos del terreno.", False,
                "Explica más, sí, y justo por eso no sirve: está hecha con los mismos puntos que "
                "intenta explicar. Una covariable que «explica» por construcción no explica nada."),
             op("Que no se puede, porque un número de vecinos es un conteo y no una medición, y rhohat "
                "solo admite covariables continuas medidas sobre el terreno.", False,
                "Admite cualquier función definida en toda la ventana —una distancia, una imagen, "
                "una función de x e y—, sea o no un conteo. El problema no es el formato, es de "
                "dónde sale."),
             op("Que vale si se restringe la curva al bulto, entre los percentiles 5 y 95, para "
                "quitarle las colas.", False,
                "Quitar las colas arregla otro problema —que la razón entre el máximo y el mínimo la "
                "decida una cola con pocos datos—, no el de una covariable que viene de los puntos.")]),

    preg("numerica", "cap5", 8,
         f"Sin covariables, <code>ppm(X ~ 1)</code> no pasa por la cuadratura; con "
         f"<code>forcefit = TRUE</code> sí pasa por ella. Kennedy mide "
         f"{cn('forzado.area_km2')}, y sobre sus {cn('forzado.n')} sedes los pesos de esa "
         f"cuadratura suman {cn('forzado.suma_pesos_km2')}. ¿Qué intensidad devuelve "
         f"<code>ppm(X ~ 1, forcefit = TRUE)</code>, en sedes por km²? Con tres decimales; se acepta "
         f"una diferencia de {n(0.005, 3)}.",
         "Escribe la log-verosimilitud aproximada con una intensidad constante y maximízala.",
         respuesta=float(cn('forzado.correcto')), tolerancia=0.005, unidad="sedes/km²",
         retroAcierto=(
             f"En el máximo, la derivada respecto del intercepto es n menos la suma de la cuadratura "
             f"—λ̂ por el peso de cada punto—, y se anula: λ̂·Σw = n. Sin covariables λ̂ es una "
             f"constante, así que λ̂ = n/Σw = {cn('forzado.correcto')}. La fórmula cerrada da "
             f"{dist('forzado', 'formula_cerrada')}: la cuadratura deja {cn('forzado.sin_contar_km2')} "
             f"de Kennedy sin contar, y el modelo reparte las {cn('forzado.n')} sedes sobre el área "
             f"que la cuadratura ve. Es la misma identidad que el módulo 8 mide en la ciudad, con "
             f"{c('c5m8_sin_contar')} sin contar, y la razón por la que dos AIC solo se comparan con "
             f"la misma cuadratura."),
         retroFallo=(
             f"Si respondiste {dist('forzado', 'formula_cerrada')}, usaste el área de la ventana: es la "
             f"fórmula cerrada, la que <code>ppm</code> usa sin forcefit. Con la cuadratura, lo que "
             f"iguala n es la suma de los pesos por λ̂, no la integral sobre la ventana entera: "
             f"λ̂ = n/Σw.")),

    preg("opcion", "cap5", 9,
         f"Con pu, las sedes del perímetro urbano, y xc e yc, sus coordenadas este y norte centradas "
         f"y en kilómetros, <code>ppm(pu ~ xc + yc)</code> da para xc un coeficiente de "
         f"{c('c5m9_xc')} con z = {c('c5m9_z_xc')}, y para yc uno de {c('c5m9_yc')} con "
         f"z = {c('c5m9_z_yc')}. ¿Qué autorizan a concluir estos coeficientes?",
         "Repasa de dónde sale el error estándar de cada coeficiente.",
         opciones=[
             op(f"Si las sedes fueran independientes, que la intensidad baja hacia el este, un "
                f"{cn('ebeta.pct_por_km')} por kilómetro; del norte-sur, nada.", True,
                f"En un <code>ppm</code> log-lineal el coeficiente se lee en escala multiplicativa: "
                f"cada kilómetro hacia el este multiplica λ por exp({c('c5m9_xc')}) = "
                f"{cn('ebeta.factor_por_km')}. El condicional es parte de la respuesta: esos errores "
                f"suponen sedes independientes, y el módulo 11 enseña que con los conglomerados dentro "
                f"la z de xc ya no llega a {c('c5m11_zc')} en valor absoluto en ninguno de los seis "
                f"ajustes de conglomerado —Thomas, Matérn y Cox log-gaussiano, cada uno con las dos "
                f"correcciones de K—; la mayor en valor absoluto, {c('c5m11_z_abs_max')}. Y no encontrar un gradiente "
                f"norte-sur no es encontrar que no lo hay."),
             # Una abstención falsa junto a la buena: la lección pide callar
             # sobre el norte-sur, y si la única que callaba era la clave, se
             # elegía por callar (forma, ronda 5).
             op("Nada de ningún coeficiente: aun si el modelo de Poisson es correcto, los dos signos "
                "negativos podrían ser azar, y sin una envolvente no se sabe cuál de los dos lo es.", False,
                f"Bajo Poisson, la z ya es la comparación con el azar del modelo: la de xc, "
                f"{c('c5m9_z_xc')}, pasa de {c('c5m11_zc')} en valor absoluto y distingue el gradiente "
                f"este-oeste. La que no llega es la de yc, {c('c5m9_z_yc')}: del norte-sur, estos "
                f"coeficientes callan, y un coeficiente que no se distingue de cero no dice hacia "
                f"dónde va."),
             op(f"Si el modelo de Poisson es correcto, que no hay gradiente norte-sur, porque la z de yc "
                f"no llega a {c('c5m11_zc')} en valor absoluto y la de xc sí.", False,
                "No llegar al valor crítico es no tener evidencia de un gradiente, no tener "
                "evidencia de que no lo hay. Los coeficientes callan sobre el norte-sur."),
             op(f"Que la intensidad baja hacia el este aun con las sedes agrupadas: una z de "
                f"{c('c5m9_z_xc')} aguanta que su error estándar se duplique.", False,
                f"La cuenta sería cierta si el error solo se duplicara, pero el agrupamiento lo "
                f"multiplica por más: con Thomas y la K de traslación, la z de xc pasa de "
                f"{c('c5m11_z_pois')} a {c('c5m11_z_th_tr')}, y el gradiente deja de distinguirse de "
                f"cero.")]),

    preg("grafico", "cap5", 10,
         f"Del Poisson inhomogéneo ajustado a las sedes —el gradiente en xc e yc— se simularon "
         f"{c('c5m10_nsim')} patrones. El gráfico divide tres curvas por la media de las K "
         f"inhomogéneas de esos {c('c5m10_nsim')} patrones: la K inhomogénea observada de las sedes y "
         f"los dos bordes de la banda del mínimo y el máximo. Así, el modelo queda en la línea del 1. "
         f"La línea vertical marca r&nbsp;=&nbsp;{c('c5m10_ultimo')}. ¿En qué distancias está lo que el modelo "
         f"no explica?",
         "Compara, radio a radio, la curva observada con los dos bordes de su banda.",
         alto=260,
         descripcionGrafico=(
             f"Tres curvas contra el radio, de {ent(KIN['r'][0])}&nbsp;m a {c('c5m10_rmax')}, "
             f"divididas por la media del modelo: el borde bajo y el alto de la banda, que encierran "
             f"el 1, y la curva observada. Una línea vertical marca {c('c5m10_ultimo')}. Observada "
             f"frente al borde alto, en algunos radios: "
             + "; ".join(f"{ent(KIN['r'][i])}&nbsp;m, {n(KIN['observada'][i], 3)} frente a "
                         f"{n(KIN['alta'][i], 3)}" for i in NODOS_KIN)
             + "."),
         dibujar="""canvas => {
            const g = DATOS_PRE2.graficos.g_kinhom;
            const corte = DATOS_PRE2.reutilizado.c5m10_ultimo.valor;
            return crearGraficoLinea(canvas, [], [
              { label: 'Observada', data: puntosXY(g.r, g.observada), borderColor: COLORES_GRAFICO.primario,
                backgroundColor: 'transparent', pointRadius: 0, borderWidth: 2.5 },
              { label: 'Banda del modelo', soloTooltip: 'Borde alto', data: puntosXY(g.r, g.alta),
                borderColor: GRIS_REFERENCIA, backgroundColor: 'rgba(100, 116, 139, 0.18)', fill: '+1',
                pointRadius: 0, borderWidth: 1 },
              { label: '', soloTooltip: 'Borde bajo', data: puntosXY(g.r, g.baja), borderColor: GRIS_REFERENCIA,
                backgroundColor: 'transparent', pointRadius: 0, borderWidth: 1 },
              { label: 'El modelo', corto: 'Modelo', data: puntosXY(g.r, g.r.map(() => 1)),
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent', borderDash: [6, 4],
                pointRadius: 0, borderWidth: 1.5 },
              // Solo para la leyenda: la marca la dibuja `marcaVertical`.
              { label: 'r = ' + milesPreparcial(corte) + ' m', data: [],
                borderColor: '#475569', backgroundColor: 'transparent', borderDash: [2, 3], borderWidth: 1.5 }
            ], { scales: { x: ejeKmPreparcial(g.r),
                           y: ejesPreparcial('', 'K observada / media del modelo', { min: 0.6, max: 2.5 }).y },
                 plugins: Object.assign(pluginsPreparcial(it => it.text !== '', { tituloRadio: true }),
                                        { marcaVertical: { x: corte } }) });
          }""",
         opciones=[
             op(f"En las escalas cortas y medias: fuera por arriba desde {c('c5m10_primer')}, y "
                f"de vuelta en la banda pasados {c('c5m10_ultimo')}.", True,
                f"Quien dice «se sale de la banda» sin decir dónde se deja la mitad útil de la "
                f"información: hasta dónde llega lo que el modelo no explica. Pasados "
                f"{c('c5m10_ultimo')}, la curva observada ya no se distingue de la del modelo, pero eso "
                f"no prueba que el gradiente explique esas distancias: la K inhomogénea del capítulo, "
                f"como la calcula <code>Kinhom</code> por defecto, divide por una λ̂ suavizada con un "
                f"núcleo de σ ≈ {cn('kinhom_nucleo.sigma_nucleo_m')} —en el dato y en cada "
                f"simulación—, y un núcleo así absorbe lo que varía a escalas de varios kilómetros. "
                f"Los dos extremos del tramo, {c('c5m10_primer')} y {c('c5m10_ultimo')}, se leen sobre "
                f"una banda puntual; la curva entera se contrasta con el DCLF."),
             op(f"Pasados {c('c5m10_ultimo')}, donde la banda se estrecha y la curva observada se "
                f"separa del 1 de forma más clara.", False,
                f"Al revés: pasados {c('c5m10_ultimo')} la observada vuelve dentro de la banda y se "
                f"sigue dentro en los {c('c5m10_nodos_dentro')} radios del barrido que quedan; lo que se sale está antes, "
                f"desde {c('c5m10_primer')}, y el mayor cociente, "
                f"{n(KIN['forma']['max_cociente'], 2)}, está a "
                f"{ent(KIN['forma']['r_max_cociente'])}&nbsp;m."),
             op("En el barrido entero: la curva observada queda por encima de la línea del 1 hasta "
                "casi el final, y eso es lo que el modelo no explica.", False,
                f"Por encima del 1 no es fuera de la banda: pasados {c('c5m10_ultimo')} la observada "
                f"sigue por encima del 1 un tramo, pero ya dentro de la banda, y termina en "
                f"{n(KIN['observada'][-1], 2)}. Lo que el modelo no explica es lo que se sale de la "
                f"banda, no lo que pasa de 1."),
             op(f"En las que cruza la banda, pero sin seguridad: {c('c5m10_fuera')} de las "
                f"{c('c5m10_nsim')} curvas del propio modelo también la cruzan, así que salirse no "
                f"distingue el dato del modelo.", False,
                f"La cifra es cierta; la conclusión, no. Esas salidas dicen que la banda, mirada en "
                f"todos los radios a la vez, no contrasta al nivel que tiene en cada radio. Para juzgar "
                f"la curva entera está el test DCLF, que da {c('c5m10_dclf')}, el mínimo posible con "
                f"{c('c5m10_nsim')} simulaciones: el exceso sobre este modelo no es azar.")]),

    preg("multiple", "cap5", 11,
         f"Se ajusta un proceso de Thomas a las sedes con <code>kppm</code> dos veces, cambiando "
         f"solo la corrección con que se estima K. Con la isotrópica sale una escala de "
         f"{c('c5m11_th_iso_esc')} y {c('c5m11_th_iso_mu')} sedes por conglomerado; con la de "
         f"traslación, {c('c5m11_th_tr_esc')} y {c('c5m11_th_tr_mu')}. Con la isotrópica, un "
         f"proceso de Matérn da una escala de {c('c5m11_mat_iso_esc')}. En Thomas, la escala es la "
         f"desviación típica, en cada eje, del desplazamiento de cada sede respecto de su centro; en "
         f"Matérn, el radio del disco donde cae. Marca todo lo que es cierto.",
         # La pista nombraba las dos claves, una por cláusula (forma, ronda 5).
         "Recuerda qué compara <code>kppm</code> cuando ajusta.",
         opciones=[
             op("El contraste mínimo ajusta el modelo a una estimación de K, así que cambiar el "
                "estimador de K cambia los parámetros del ajuste.", True,
                f"Las sedes por conglomerado cambian un {c('c5m11_mu_pct')}: la función que el "
                f"contraste mínimo minimiza es casi plana cerca de su mínimo, y un cambio pequeño en "
                f"la K empírica mueve mucho dónde cae. Un ajuste de conglomerado sin decir con qué K "
                f"se hizo está incompleto."),
             op(f"Con la isotrópica el ajuste tarda {c('c5m11_th_iso_seg')}, y con la de traslación, "
                f"{c('c5m11_th_tr_seg')}: por defecto usa la isotrópica, la cara, sin decirlo.", True,
                f"Si la llamada no nombra la corrección, <code>kppm</code> pide a <code>Kest</code> la "
                f"«mejor» (<code>correction = \"best\"</code>), que sobre una ventana poligonal como "
                f"esta es la isotrópica: sobre sus {c('c4m10_vertices')} vértices, la cara. No la anota "
                f"entre los argumentos del ajuste ni la imprime; solo queda en el nombre de la columna, "
                f"<code>iso</code>, de la K que el objeto guarda dentro. Cambiarla no solo acelera el "
                f"ajuste: cambia la respuesta, y por eso se escribe en la llamada."),
             op(f"Matérn saca conglomerados casi el doble de anchos que Thomas con la misma "
                f"corrección: su escala, {c('c5m11_mat_iso_esc')}, casi dobla la de "
                f"{c('c5m11_th_iso_esc')}.", False,
                f"Las dos escalas no miden lo mismo. Pasadas a la distancia media de una sede a su "
                f"centro —la escala de Thomas por √(π/2), y dos tercios del radio de Matérn— dan "
                f"{cn('escalas.thomas_media_m')} y {cn('escalas.matern_media_m')}: casi lo mismo. Y "
                f"las sedes por conglomerado, {c('c5m11_th_iso_mu')} frente a "
                f"{c('c5m11_mat_iso_mu')}. La familia mueve poco; el estimador de K mueve mucho."),
             op("Uno de los dos ajustes de Thomas es el correcto: hay que quedarse con el de la "
                "isotrópica, que es la corrección más exacta.", False,
                "Ninguno es «el» correcto: los dos ajustan el mismo modelo a dos estimaciones "
                "legítimas de K. Lo que es obligatorio es decir cuál se usó."),
             op(f"La diferencia la ponen las {c('c5m11_repetidas')} sedes que repiten coordenadas, que "
                f"la isotrópica cuenta y la de traslación deja fuera.", False,
                f"Las dos correcciones cuentan las mismas parejas, duplicadas incluidas; lo que cambia "
                f"es cómo las pesan. Y quitando las duplicadas, el mayor cambio de un parámetro es de "
                f"un {c('c5m11_dup_cambio')}, muy lejos del {c('c5m11_mu_pct')} que pone cambiar de "
                f"corrección.")],
         giro=2),
]


# ---------------------------------------------------------------------
# BLOQUE C · los dos capítulos a la vez. Cada pregunta declara el módulo al
# que conviene volver PRIMERO, que es el del capítulo 5 donde se resuelve
# lo que el capítulo 4 dejó planteado.
# ---------------------------------------------------------------------
DOS = GR["g_dos"]
FD = DOS["forma"]
NODOS_DOS = sorted({0} | {min(range(len(DOS["r"])), key=lambda i, d=d: abs(DOS["r"][i] - d))
                          for d in (1000, 2000, val("c5m10_ultimo"))} | {len(DOS["r"]) - 1})

BLOQUE_C = [
    preg("grafico", "cap5", 10,
         f"El gráfico pone las sedes contra dos referencias. En naranja, la K del capítulo 4 "
         f"dividida por πr², con la banda del mínimo y el máximo de {c('c4m11_nsim')} simulaciones "
         f"de CSR. En verde, la K inhomogénea del capítulo 5 dividida por la media de su modelo "
         f"ajustado, con la banda del mínimo y el máximo de {c('c5m10_nsim')} simulaciones de ese "
         f"modelo. ¿Qué parte del exceso que se veía contra CSR desaparece en la curva verde?",
         "Compara, en el primer radio y en el último, cuánto pasa de 1 cada curva y si queda dentro "
         "de su banda.",
         alto=270,
         descripcionGrafico=(
             f"Dos curvas con su banda, contra el radio, de {ent(DOS['r'][0])}&nbsp;m a "
             f"{c('c5m10_rmax')}. En algunos radios, la naranja y el borde alto de su banda, y "
             f"después la verde y el borde alto de la suya: "
             + "; ".join(f"{ent(DOS['r'][i])}&nbsp;m, naranja {n(DOS['csr_observada'][i], 3)} "
                         f"(banda hasta {n(DOS['csr_alta'][i], 3)}), verde "
                         f"{n(DOS['mod_observada'][i], 3)} (banda hasta {n(DOS['mod_alta'][i], 3)})"
                         for i in NODOS_DOS)
             + "."),
         dibujar="""canvas => {
            const g = DATOS_PRE2.graficos.g_dos;
            const VERDE = '#1a7358', NARANJA_BORDE = '#ea580c';
            return crearGraficoLinea(canvas, [], [
              { label: 'Contra CSR', corto: 'CSR', data: puntosXY(g.r, g.csr_observada),
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent', pointRadius: 0,
                borderWidth: 2.5 },
              // La banda de CSR va sin relleno, solo con sus bordes a rayas: las
              // dos bandas se pisaban casi enteras y daban un beige gris en el
              // que la verde no se veía verde. Los bordes, en un naranja que
              // pasa el 3:1 (el anterior, al 60 %, daba 1.96:1), porque son los
              // que la pista manda comparar (gráficos, ronda 5).
              { label: 'su banda', soloTooltip: 'Contra CSR, borde alto', corto: 'CSR, alto',
                data: puntosXY(g.r, g.csr_alta), borderColor: NARANJA_BORDE, borderDash: [5, 3],
                backgroundColor: 'transparent', pointRadius: 0, borderWidth: 1.25 },
              { label: '', soloTooltip: 'Contra CSR, borde bajo', corto: 'CSR, bajo',
                data: puntosXY(g.r, g.csr_baja), borderColor: NARANJA_BORDE, borderDash: [5, 3],
                backgroundColor: 'transparent', pointRadius: 0, borderWidth: 1.25 },
              { label: 'Contra el modelo', corto: 'Modelo', data: puntosXY(g.r, g.mod_observada),
                borderColor: VERDE, backgroundColor: 'transparent', pointRadius: 0, borderWidth: 2.5 },
              { label: 'su banda', soloTooltip: 'Contra el modelo, borde alto', corto: 'Modelo, alto',
                data: puntosXY(g.r, g.mod_alta), borderColor: 'rgba(26, 115, 88, 0.7)',
                backgroundColor: 'rgba(26, 115, 88, 0.14)', fill: '+1', pointRadius: 0, borderWidth: 1 },
              { label: '', soloTooltip: 'Contra el modelo, borde bajo', corto: 'Modelo, bajo',
                data: puntosXY(g.r, g.mod_baja), borderColor: 'rgba(26, 115, 88, 0.7)',
                backgroundColor: 'transparent', pointRadius: 0, borderWidth: 1 }
            ], { scales: { x: ejeKmPreparcial(g.r), y: ejesPreparcial('', 'K observada / referencia').y },
                 plugins: pluginsPreparcial(it => it.text !== '', { tituloRadio: true }) });
          }""",
         opciones=[
             op("Todo a las distancias largas y poco a las cortas: al final solo la naranja sigue "
                "fuera, y al principio las curvas casi coinciden.", True,
                f"En el primer radio del barrido el exceso sobre 1 baja de {n(FD['exceso_csr_primera'], 3)} a "
                f"{n(FD['exceso_mod_primera'], 3)}: casi no cambia. En el último, de "
                f"{n(FD['exceso_csr_ultima'], 2)} a nada: la verde termina en {n(FD['mod_ultima'], 2)}, "
                f"dentro de su banda. Es la bisagra del capítulo 5: contra CSR, atracción e intensidad "
                f"variable dejan la misma huella; contra una referencia que ya lleva la intensidad "
                f"dentro, no. Ojo con quién se lleva el exceso de las distancias largas: la K "
                f"inhomogénea del capítulo divide cada pareja por una λ̂ suavizada de las propias sedes "
                f"—la que <code>Kinhom</code> estima por defecto, con un núcleo de σ ≈ "
                f"{cn('kinhom_nucleo.sigma_nucleo_m')}—, no por el gradiente del modelo, y un núcleo de "
                f"ese ancho se traga, en el dato y en cada simulación, lo que varía a escalas de varios "
                f"kilómetros. Lo que el exceso hasta {c('c5m10_ultimo')} sí dice es que el modelo "
                f"ajustado no reproduce la agregación a escalas cortas y medias, y por eso el capítulo "
                f"prueba después un proceso de conglomerado."),
             op("Todo: contra su propio modelo, la curva verde vuelve a su banda en todas las "
                "distancias del barrido, de punta a punta.", False,
                f"Vuelve solo pasados {c('c5m10_ultimo')}; antes está fuera, por arriba, empezando "
                f"en {n(FD['mod_primera'], 2)}."),
             op("Una fracción parecida en todas las distancias, porque el modelo divide la curva "
                "entera por un mismo factor de escala.", False,
                f"El divisor apenas cambia: la media de las K inhomogéneas del modelo se separa de πr² "
                f"como mucho un {c('c5m10_mmean_pct')}, así que las dos curvas se dividen casi por lo "
                f"mismo. Lo que cambia es la curva: la K inhomogénea divide cada pareja por la "
                f"intensidad estimada en sus dos puntos, y eso no quita lo mismo en cada radio: casi "
                f"nada en el primer radio del barrido, y todo en el último."),
             op("Mucho en las distancias cortas y poco en las largas, donde la curva verde sigue fuera "
                "de su banda hasta el final del barrido.", False,
                f"Al revés: en el primer radio del barrido las dos casi coinciden, "
                f"{n(FD['csr_primera'], 2)} y {n(FD['mod_primera'], 2)}, y al final la verde, en "
                f"{n(FD['mod_ultima'], 2)}, está dentro de su banda.")]),

    preg("multiple", "cap5", 4,
         "«Corrección de borde» aparece en los dos capítulos y no nombra lo mismo. Marca todo lo "
         "que es cierto.",
         "Para cada estimador, piensa qué hace la corrección y dónde se nota.",
         opciones=[
             op(f"Calcular K con la isotrópica cuesta {c('c4m10_veces_iso')} veces lo que con la de "
                f"traslación sobre la ventana urbana; en la KDE, corregir o no cuesta casi lo mismo.",
                True,
                f"Corregir K cuesta según el contorno: la isotrópica corta un círculo contra el "
                f"contorno, pareja a pareja, y su coste crece con los vértices, {c('c4m10_vertices')} "
                f"en la ventana urbana. Una envolvente de 999 con ella costaría {c('c4m10_horas_iso')}, "
                f"frente a {c('c4m10_min_trans')} con la de traslación. En la KDE la corrección es una "
                f"convolución más sobre la rejilla del mapa, y su coste crece con los píxeles, no con "
                f"el contorno. La misma expresión nombra una operación cara y una casi gratis."),
             op("Sin corregir, K pierde vecinos y la KDE pierde masa: los dos estimadores se quedan "
                "cortos cerca del borde.", True,
                "Faltan los vecinos de fuera de la ventana y se pierde la parte del núcleo que se "
                "sale: en los dos casos, lo que falta es lo que cae fuera de la ventana, donde no se "
                "observó. En K, eso empuja la conclusión hacia «más regular»."),
             op("La corrección de K se elige solo por lo que cuesta, porque todas dan la misma curva; "
                "la de la KDE, por la masa, porque no todas integran n.", False,
                f"No dan la misma curva. Sin corregir, la K de las sedes llega a quedarse un "
                f"{c('c4m10_sesgo')} por debajo de la corregida por traslación. Entre la isotrópica y "
                f"la de traslación hay hasta un {cn('iso_tras.max_dif_pct')}, a "
                f"{cn('iso_tras.r_max_dif_m')}: poco para leer la curva, y bastante para que "
                f"<code>kppm</code> cambie un {c('c5m11_mu_pct')} las sedes por conglomerado. El "
                f"coste entra en la decisión, pero no la toma solo."),
             op("En los dos capítulos, la corrección por defecto conserva lo que hay: en K, las "
                "parejas; en la KDE, el número de puntos.", False,
                "La KDE con la corrección por defecto no conserva el número de puntos: con unas "
                "posiciones se pasa y con otras se queda corta, y la única que lo conserva siempre es "
                "la de Diggle. Y en K tampoco se trata de conservar parejas: se pesan para compensar "
                "las que no se observaron."),
             op(f"En la KDE la corrección pesa solo cerca del borde; en K, sobre todo a distancias "
                f"cortas, donde la K sin corregir llega a quedarse un {c('c4m10_sesgo')} por debajo.",
                False,
                f"La primera mitad es cierta si «cerca» se mide en anchos de banda: la corrección pesa a "
                f"unos pocos σ del borde. La segunda, al revés: en K el efecto del borde crece "
                f"con r, porque a r grande más discos tocan el borde. En las sedes, ese "
                f"{c('c4m10_sesgo')} —lo que K sin corregir se queda por debajo— se da en la distancia "
                f"más larga del barrido, {c('c4m10_r_sesgo')}.")],
         giro=3),

    preg("opcion", "cap5", 10,
         f"En el capítulo 4, el {c('c4m11_tasa_bog')} de las simulaciones de CSR de las sedes se "
         f"sale en algún r de una banda de cuantiles centrales de cobertura "
         f"{cn('niveles.cap4_cobertura_pct')}, construida con las {c('c4m11_nsim')}; en el "
         f"capítulo 5, el {c('c5m10_tasa')} de las curvas del modelo cruza en algún radio la banda "
         f"del mínimo y el máximo de las demás. En los dos casos las curvas se simularon del propio "
         f"modelo nulo, que por construcción es el verdadero. ¿Qué explica sobre todo la diferencia?",
         "Piensa en cómo se construyó cada banda a partir de las simulaciones.",
         opciones=[
             op(f"Que las bandas no tienen el mismo nivel puntual: la del capítulo 4 contrasta al "
                f"{cn('niveles.cap4_pct')} en cada r, y la del 5, con el mínimo y el máximo, al "
                f"{c('c5m10_nivel')}.", True,
                f"Con las mismas {c('c4m11_nsim')} simulaciones, una banda de cuantiles de cobertura "
                f"{cn('niveles.cap4_cobertura_pct')} deja fuera, en cada r, al "
                f"{cn('niveles.cap4_pct')} de las curvas; la del mínimo y el máximo, al "
                f"{c('c5m10_nivel')}. Ojo: la banda que el capítulo 4 dibuja en su módulo 11 es también "
                f"la del mínimo y el máximo; la tasa del {c('c4m11_tasa_bog')} se midió contra la de "
                f"cuantiles. En las dos, mirar cientos de radios a la vez hace que la tasa supere de "
                f"lejos el nivel puntual: es la lección común del módulo 11 del capítulo 4 y del 10 "
                f"del capítulo 5."),
             op("Que en el capítulo 5 las curvas y la banda se dividen por la media del modelo, y "
                "dividir así deja menos sitio para salirse.", False,
                "Dividir todas las curvas y los dos bordes por la misma función positiva no cambia "
                "quién cruza la banda: solo cambia la escala del dibujo. Lo que cambia la tasa es el "
                "nivel puntual de la banda."),
             op("Que las curvas del modelo ajustado se parecen más entre sí que las de CSR, porque "
                "todas llevan la misma intensidad, y pocas se apartan de las demás.", False,
                "Las de CSR también llevan todas la misma intensidad, y cuánto se parezcan entre sí no "
                "cambia cuántas se salen de una banda hecha con ellas mismas: eso lo fijan el nivel "
                "puntual de la banda y cuántos radios se miran."),
             # Antes se contradecía sola («una banda que incluye a la curva la
             # deja salirse más») y se descartaba sin saber nada (forma, ronda
             # 5). Ahora los hechos y el mecanismo son ciertos, y lo que falla
             # es la dirección: hay que cotejarla con las dos tasas.
             op("Que la banda del capítulo 5 se construye sin la curva que se juzga y la del 4 con "
                "todas: una banda hecha sin la curva la deja salirse más a menudo, y eso explica la "
                "diferencia.", False,
                f"La construcción es esa, y una banda hecha sin la curva la deja salirse más a menudo. "
                f"Pero eso empujaría hacia arriba la tasa del capítulo 5, y es la menor: el "
                f"{c('c5m10_tasa')} frente al {c('c4m11_tasa_bog')}. Lo que separa las tasas es el "
                f"nivel puntual.")]),

    preg("opcion", "cap5", 2,
         "El tamaño del cuadrante del capítulo 4 y el ancho de banda del capítulo 5 hacen papeles "
         "parecidos. ¿En qué se parecen y en qué no?",
         "Piensa en qué decide cada uno, y en quién lo decide.",
         opciones=[
             op("Los dos fijan la escala y la teoría no dicta ninguno; difieren en que las vecindades "
                "del núcleo se solapan y no tienen bordes rectos.", True,
                f"Es el MAUP del capítulo 3, dos veces. Con el cuadrante, el veredicto sobre las "
                f"secuoyas cambia con la celda: entre las rejillas que respetan el supuesto del χ² —que "
                f"ninguna celda espere menos de 5—, la "
                f"{ej(val_nuevo('supuesto_rw.nx_no_rechaza_con_supuesto')[0])} no rechaza y la "
                f"{ej(val_nuevo('supuesto_rw.nx_con_supuesto')[0])} sí. Con el ancho, el pico de "
                f"Kennedy cae un {c('c5m2_caida')}. El núcleo quita los bordes rectos y deja solaparse "
                f"a las vecindades, pero no quita la decisión."),
             op("Los dos fijan la escala y la teoría no dicta ninguno; difieren en que el ancho solo "
                "cambia lo suave que se ve el mapa, no lo que dice, y el cuadrante cambia el veredicto.",
                False,
                f"El ancho decide lo que el mapa dice, no solo cómo se ve: el pico cae un "
                f"{c('c5m2_caida')} del más estrecho al más ancho, y con él cambia dónde parece haber "
                f"más sedes. No es presentación."),
             op("Los dos fijan la escala, y un selector automático encuentra el mejor valor de cada "
                "uno; difieren en que el del cuadrante es más difícil de calcular.", False,
                f"En el cuadrante no hay selector, y sobre la ciudad el mayor de los cuatro selectores "
                f"de ancho llega a {c('c5m3_razon_urb')} veces el menor: cada uno contesta otra "
                f"pregunta. El ancho se elige y se declara."),
             op("Los dos fijan la escala y la teoría no dicta ninguno; difieren en que el ancho se "
                "fija con el número de celdas del mapa, y el cuadrante lo elige quien analiza.", False,
                "La segunda mitad es cierta, y por eso la diferencia no está ahí: el ancho también lo "
                "elige quien analiza. La rejilla del mapa solo limita el ancho más estrecho que se "
                "puede dibujar sin mentir; no lo elige.")]),

    preg("numerica", "cap5", 11,
         f"Con un proceso de Matérn y la K isotrópica, el error estándar del coeficiente de xc es "
         f"{c('c5m11_mat_iso_inf')} veces el del Poisson. ¿A cuántas sedes independientes equivalen "
         f"las {c('c5m11_n')} sedes para estimar ese gradiente? Con un decimal; se acepta una "
         f"diferencia de {n(0.5, 1)}.",
         "Repasa cómo definió el capítulo 1 el efecto de diseño.",
         respuesta=float(n(val_nuevo("n_efectivo.correcto"), 1)), tolerancia=0.5, unidad="sedes",
         retroAcierto=(
             f"El efecto de diseño es el cuadrado del cociente de errores estándar, "
             f"{cn('n_efectivo.efecto_diseno')}, y el tamaño efectivo es n dividido por él: "
             f"{cn('n_efectivo.correcto')}. Es la cuenta del capítulo 1, ahora con un coeficiente; "
             f"para Thomas con la K de traslación, el capítulo 5 dice que las {c('c5m11_n')} sedes "
             f"informan del gradiente como {c('c5m11_neff')} independientes, con un efecto de diseño "
             f"de {c('c5m11_deff')}. Y la corrección de K también pesa aquí: con Thomas, el error "
             f"estándar de xc se multiplica por {c('c5m11_th_iso_inf')} con la isotrópica y por "
             f"{c('c5m11_th_tr_inf')} con la de traslación."),
         retroFallo=(
             f"El tamaño efectivo es n dividido por el efecto de diseño, que es el cuadrado del "
             f"cociente de errores estándar. Si respondiste {dist('n_efectivo', 'sin_cuadrado')}, "
             f"no elevaste al cuadrado; si respondiste {dist('n_efectivo', 'el_de_thomas')}, "
             f"tomaste el del ajuste de Thomas con la K de traslación, que es el que publica el "
             f"capítulo.")),

    preg("multiple", "cap5", 8,
         "Sobre el papel de la ventana de observación en los estimadores de los capítulos 4 y 5, "
         "marca todo lo que es cierto.",
         # La pista ya no presupone que la ventana entra en todos: las dos
         # falsas eran justo las que decían que no, y el conjunto salía sin
         # saber nada. Ahora una falsa dice que entra, y en todos igual
         # (forma, ronda 5).
         "Recorre los estimadores uno por uno —λ̂, F, K, la KDE y <code>ppm</code>— y pregúntate, en "
         "cada uno, si usa la ventana y para qué.",
         opciones=[
             op(f"En F, solo cuentan como sitios desde los que medir los que caen dentro de la "
                f"ventana: de los {c('c4m7_f_rejilla')} de la rejilla de Bogotá, "
                f"{c('c4m7_f_sitios')}.", True,
                "Un sitio fuera de la ventana no está vacío: está sin observar, y contarlo como "
                "hueco haría salir la F más baja. Es la lección del módulo 1 aplicada a los sitios."),
             op(f"En ppm, la cuadratura por defecto deja {c('c5m8_sin_contar')} de ciudad sin "
                f"contar, y esa área llega al AIC.", True,
                f"Los pesos de la cuadratura suman {c('c5m8_suma_pesos')} cuando la ciudad mide "
                f"{c('c5m8_area')}. El intercepto hace que la suma de la cuadratura dé exactamente las "
                f"{c('c4m1_n_urb')} sedes; integrado después sobre la ciudad entera, un ajuste con la "
                f"distancia al centro como covariable pone {c('c5m8_esperadas')}, no "
                f"{c('c4m1_n_urb')}. Eso mueve la verosimilitud, y con ella el AIC, sin que cambie "
                f"el modelo."),
             op("En la KDE, el divisor e(u) de la corrección de borde es la parte de la masa del "
                "núcleo centrado en u que no se sale de la ventana.", True,
                "Sin dividir por e(u), la masa de los núcleos que se sale se pierde; la corrección "
                "por defecto la compensa en cada sitio del mapa donde estima, y la de Diggle en cada "
                "punto del patrón."),
             # Sin absoluto: las dos falsas eran justo las dos con «solo» y «en
             # todas del mismo modo», y el conjunto salía por la regla
             # «absoluta = falsa» (redacción, ronda 5).
             # Contraria a la de «en todas del mismo modo», y falsa como ella: un
             # par que se contradice sin clave (H17, ronda 5).
             op("En K la ventana no hace falta: K compara distancias entre puntos, y la distancia entre "
                "dos sedes es la misma dentro de cualquier ventana.",
                False,
                "Hace falta dos veces: en λ̂, que divide la cuenta de parejas, y en la corrección de "
                "borde, que pesa cada pareja según cuánto de su círculo, o de la ventana desplazada, "
                "queda dentro. Sin la ventana, K no sabría qué parejas se quedaron sin observar, y "
                "saldría más baja cuanto más lejos mira."),
             op("La ventana entra en λ̂ = n/|W| y en las funciones de distancia, y en todas del mismo "
                "modo: dividiendo por su área, |W|.", False,
                "Entra en todas, pero no del mismo modo: en F, por los sitios desde los que se mide; "
                "en K, por los pesos de cada pareja; en la KDE, por el divisor e(u); en ppm, por la "
                "cuadratura. Es la idea con que abre el capítulo 4: la ventana es parte del "
                "estimador, y cada estimador la usa a su manera.")]),
]


PREGUNTAS = {"a": BLOQUE_A, "b": BLOQUE_B, "c": BLOQUE_C}


# =====================================================================
# EL ORDEN DE LAS OPCIONES SE DECIDE AQUÍ (§12.6 del plan del Corte I).
# Escritas de una en una, las preguntas tienen la correcta delante; se
# barajan con una semilla que sale del JSON y de la identidad de la
# pregunta, así que el orden es reproducible byte a byte. Ninguna
# retroalimentación puede nombrar una posición: lo vigila `POSICIONALES`.
# =====================================================================
def baraja(identidad, opciones):
    r = random.Random(f"{meta['semilla']}·{identidad}")
    orden = list(range(len(opciones)))
    r.shuffle(orden)
    return [opciones[i] for i in orden]


# `giro` cambia la semilla de UNA pregunta y nada más. Existe por las de
# varias respuestas: barajadas sin más, la «a» salía clave en seis de las ocho
# (ronda 4), y quien lo nota marca la «a» sin leer. La guarda de abajo lo
# vigila, y el giro de cada una está escrito junto a ella.
for _clave, _preguntas in PREGUNTAS.items():
    for _i, _q in enumerate(_preguntas, 1):
        if "opciones" in _q:
            _giro = f"·{_q['giro']}" if _q.get("giro") else ""
            _q["opciones"] = baraja(f"{_clave}{_i}·{_q['doc']}.m{_q['modulo']}{_giro}", _q["opciones"])


# =====================================================================
# EL CUESTIONARIO: emisión y guardas
# =====================================================================
def js_str(x):
    return json.dumps(x, ensure_ascii=False)


def _titulo_modulo(doc, modulo):
    return next(f["titulo"] for f in ALC.ALCANCE if f["doc"] == doc and f["modulo"] == modulo)


def _sin_marcado(t):
    return re.sub(r"<[^>]+>", "", t)


def _texto_plano(t):
    import html as _h
    return _h.unescape(_sin_marcado(t))


def js_pregunta(q):
    """Una pregunta, como el objeto que el motor espera.

    El `repaso` se arma aquí: capítulo y módulo del CAPÍTULO, con `orden`
    para que la lista del resumen salga en el orden del temario (sin él,
    el desempate alfabético daba «módulo 1, 10, 11, 2…», §12 del Corte I).
    La etiqueta va sin marcado: el título del módulo 9 del capítulo 5 lleva
    un <code> y el motor la pinta como texto.
    """
    etiqueta = (f"Cap. {q['doc'][3]} · módulo {q['modulo']} — "
                f"{_sin_marcado(_titulo_modulo(q['doc'], q['modulo']))}")
    campos = [
        f"        tipo: {js_str(q['tipo'])}",
        f"        repaso: {{ orden: {int(q['doc'][3]) * 100 + q['modulo']}, "
        f"etiqueta: {js_str(etiqueta)}, href: {js_str(ALC.DOCS[q['doc']])} }}",
        f"        pregunta: {js_str(q['pregunta'])}",
        f"        pista: {js_str(q['pista'])}",
    ]
    if q["tipo"] == "grafico":
        campos.append(f"        alto: {q['alto']}")
        # El motor la pone como `aria-label` con setAttribute, y en un atributo
        # asignado desde JavaScript las entidades no se decodifican: «&nbsp;»
        # llegaba literal a quien usa lector de pantalla. Va como texto plano.
        campos.append(f"        descripcionGrafico: {js_str(_texto_plano(q['descripcionGrafico']))}")
        campos.append(f"        dibujar: {q['dibujar']}")
    if "respuesta" in q:
        campos.append(f"        respuesta: {q['respuesta']!r}")
        campos.append(f"        tolerancia: {q['tolerancia']!r}")
        # El motor la pone junto a la casilla y detrás de la respuesta
        # revelada: «La respuesta es 2500» no decía en qué (redacción, ronda 5).
        if q.get("unidad"):
            campos.append(f"        unidad: {js_str(q['unidad'])}")
    if "opciones" in q:
        ops = ",\n".join(
            f"          {{ texto: {js_str(o['texto'])}, "
            f"correcta: {'true' if o['correcta'] else 'false'},\n"
            f"            retro: {js_str(o['retro'])} }}"
            for o in q["opciones"])
        campos.append("        opciones: [\n" + ops + "\n        ]")
    for extra in ("retroAcierto", "retroFallo"):
        if extra in q:
            campos.append(f"        {extra}: {js_str(q[extra])}")
    return "      {\n" + ",\n".join(campos) + "\n      }"


POSICIONALES = [
    re.compile(r"\blas (dos|tres|cuatro) primeras\b", re.I),
    re.compile(r"\bla (primera|segunda|tercera|cuarta|última) opción\b", re.I),
    re.compile(r"\bla opción [a-e]\)", re.I),
    re.compile(r"\blas primeras\b", re.I),
    re.compile(r"\bla de arriba\b|\bla de abajo\b", re.I),
    re.compile(r"\bque la anterior\b|\bla opción siguiente\b|\bla de antes\b", re.I),
]

# §13.5 del plan del Corte I: con esta regla se habrían cazado de golpe los
# veinte ítems cuya clave se adivinaba por ser la más larga.
MARGEN_LONGITUD = 20


def revisa_preguntas():
    """Lo que no se puede dejar a que alguien lo relea."""
    problemas = []
    for bloque, preguntas in PREGUNTAS.items():
        tipos = {q["tipo"] for q in preguntas}
        faltan = {"opcion", "multiple", "numerica", "grafico"} - tipos
        if faltan:
            problemas.append(f"al bloque {bloque.upper()} le faltan tipos: {', '.join(sorted(faltan))}")
        for i, q in enumerate(preguntas, 1):
            ref = f"{bloque.upper()}{i} ({q['doc']}.m{q['modulo']})"
            if not q.get("pista"):
                problemas.append(f"{ref}: sin pista")
            if q["tipo"] == "numerica":
                if "respuesta" not in q or "tolerancia" not in q:
                    problemas.append(f"{ref}: numérica sin respuesta o sin tolerancia")
                if not q.get("retroFallo") or not q.get("retroAcierto"):
                    problemas.append(f"{ref}: numérica sin retroAcierto o sin retroFallo")
                continue
            ops = q.get("opciones")
            if not ops:
                problemas.append(f"{ref}: sin opciones")
                continue
            correctas = [o for o in ops if o["correcta"]]
            if q["tipo"] in ("opcion", "grafico") and len(correctas) != 1:
                problemas.append(f"{ref}: {len(correctas)} opciones correctas, se esperaba 1")
            if q["tipo"] == "multiple" and len(correctas) < 2:
                problemas.append(f"{ref}: una «varias respuestas» con {len(correctas)} correcta(s)")
            retros = [o.get("retro", "") for o in ops]
            if any(not r.strip() for r in retros):
                problemas.append(f"{ref}: una opción sin retroalimentación")
            if len(set(retros)) != len(retros):
                problemas.append(f"{ref}: dos opciones comparten retroalimentación")
            for o in correctas:
                limpio = _sin_marcado(o["texto"]).strip(" .")
                if len(limpio) > 25 and limpio.lower() in q["pregunta"].lower():
                    problemas.append(f"{ref}: el enunciado contiene el texto de la correcta")
            if q["tipo"] in ("opcion", "grafico"):
                lc = len(_sin_marcado(correctas[0]["texto"]))
                ld = max(len(_sin_marcado(o["texto"])) for o in ops if not o["correcta"])
                if lc - ld > MARGEN_LONGITUD:
                    problemas.append(f"{ref}: la correcta mide {lc} caracteres y el distractor más "
                                     f"largo {ld}: se adivina por la longitud")
            textos = [q["pregunta"], q.get("pista", "")] + retros
            for texto in textos:
                for pat in POSICIONALES:
                    if pat.search(texto):
                        problemas.append(f"{ref}: nombra una posición («{pat.search(texto).group(0)}»)")
                        break

    # Sobre el documento entero: dónde cae la correcta y cuántas veces es la
    # más larga. Las dos se miran juntas porque las dos se aprueban sin leer.
    posiciones, n_una, n_larga = {}, 0, 0
    for preguntas in PREGUNTAS.values():
        for q in preguntas:
            ops = q.get("opciones")
            if not ops or q["tipo"] == "multiple":
                continue
            n_una += 1
            i = next(j for j, o in enumerate(ops, 1) if o["correcta"])
            posiciones[i] = posiciones.get(i, 0) + 1
            largos = [len(_sin_marcado(o["texto"])) for o in ops]
            if largos[i - 1] == max(largos):
                n_larga += 1
    # Las de varias respuestas, aparte: ninguna letra puede ser clave en más
    # de la mitad de ellas, ni un mismo patrón de claves repetirse más de dos
    # veces.
    letras, patrones, n_mult = {}, {}, 0
    for preguntas in PREGUNTAS.values():
        for q in preguntas:
            if q["tipo"] != "multiple":
                continue
            n_mult += 1
            pat = "".join("1" if o["correcta"] else "0" for o in q["opciones"])
            patrones[pat] = patrones.get(pat, 0) + 1
            for j, o in enumerate(q["opciones"]):
                if o["correcta"]:
                    letras["abcde"[j]] = letras.get("abcde"[j], 0) + 1
    if n_mult:
        peor_l, veces_l = max(letras.items(), key=lambda kv: kv[1])
        if veces_l > n_mult / 2:
            problemas.append(f"en las de varias respuestas, la «{peor_l}» es clave en {veces_l} de "
                             f"{n_mult}: se marca sin leer")
        repetidos = [k for k, v in patrones.items() if v > 2]
        if repetidos:
            problemas.append(f"en las de varias respuestas, el patrón {repetidos[0]} se repite "
                             f"{patrones[repetidos[0]]} veces")
    if n_una:
        peor, veces = max(posiciones.items(), key=lambda kv: kv[1])
        reparto = " · ".join(f"{k}: {v}" for k, v in sorted(posiciones.items()))
        if veces > n_una * 0.5:
            problemas.append(f"la correcta cae {veces} de {n_una} veces en la posición {peor} "
                             f"({reparto}): se puede aprobar sin leer")
        if n_larga > n_una * 0.5:
            problemas.append(f"la correcta es la opción más larga en {n_larga} de {n_una} "
                             f"preguntas de una respuesta: se puede aprobar sin leer")
    return problemas


def bloque_quiz(clave, titulo, nota):
    return f"""      <div class="quiz" data-quiz="{clave}">
        <h4><i class="fas fa-circle-question" aria-hidden="true"></i> {titulo}</h4>
        <p class="text-sm" style="margin-bottom:0;">{nota}</p>
        <div class="quiz-progreso" role="presentation"><div class="quiz-progreso-barra"></div></div>
        <div class="quiz-preguntas"></div>
        <div class="quiz-resumen" role="status" hidden></div>
        <div class="quiz-marcador">
          <span class="quiz-conteo"></span>
          <button type="button" class="quiz-reiniciar">Reiniciar</button>
        </div>
      </div>
"""


def mod_bloque_a(num):
    return cabecera(
        num, "Bloque A · Patrones puntuales", "Block A",
        "Los once módulos del capítulo 4: qué es la ventana, qué mide cada resumen, qué no ve "
        "cada uno y cuánto se mueve el azar.") + f"""
      <p>Once preguntas, una por módulo del capítulo 4, en el orden del capítulo: si una te para
        en seco ya sabes a qué módulo volver, y al terminar, el recuento final te dirá cuál, con
        el enlace al capítulo.</p>

      <p>Casi ninguna pregunta va sobre cuánto vale una cifra. Van sobre <strong>qué se puede
        concluir de ella y qué no</strong>: qué rechaza un test, qué no ve una función, hacia
        dónde empuja un sesgo. El capítulo entero defiende una idea —la pregunta «¿está
        agrupado?» no tiene respuesta hasta que se fijan la ventana, la escala, la corrección
        de borde y la referencia— y este bloque la pone a prueba once veces.</p>

{bloque_quiz("bloque-a", "Bloque A · capítulo 4",
             "Once preguntas de los cuatro tipos. Las numéricas aceptan coma o punto decimal, "
             "y la tolerancia va dicha en el enunciado.")}
      <p>El bloque siguiente hace lo mismo con el capítulo 5, donde la intensidad deja de ser un
        número y pasa a ser una superficie, y después un modelo.</p>
{CIERRE}"""


def mod_bloque_b(num):
    return cabecera(
        num, "Bloque B · Intensidad y modelos", "Block B",
        "Los once módulos del capítulo 5: estimar la intensidad, elegirle el ancho, "
        "corregirle el borde, modelarla y leer lo ajustado sin creerle de más.") + f"""
      <p>Once preguntas más, una por módulo del capítulo 5. Este capítulo tiene una
        particularidad que conviene tener presente al responder: casi todo lo que sale mal en él
        <strong>devuelve algo plausible</strong>. Un selector que chocó con el tope de su
        intervalo devuelve un número normal; una corrección que no conserva la masa dibuja un
        mapa normal; un ajuste singular devuelve coeficientes normales.</p>

      <p>Por eso varias preguntas no te piden calcular sino reconocer, por un síntoma, qué
        decisión se tomó sin declararla. Es la competencia que el capítulo entrena de verdad.</p>

{bloque_quiz("bloque-b", "Bloque B · capítulo 5",
             "Once preguntas de los cuatro tipos. Las numéricas aceptan coma o punto decimal, "
             "y la tolerancia va dicha en el enunciado.")}
      <p>Con los dos bloques hechos ya tienes medido dónde estás en cada capítulo. Antes del
        bloque que los cruza vienen las seis rutinas que el parcial puede pedirte que escribas o
        que leas, con la salida que de verdad devuelven: tres de ellas —la banda y su nivel, la
        masa de la KDE y <code>kppm</code>— son justo lo que el bloque C pone a cruzar.</p>
{CIERRE}"""


def mod_bloque_c(num):
    return cabecera(
        num, "Bloque C · Los dos capítulos a la vez", "Block C",
        "Reconocer un problema que se plantea en un capítulo y se resuelve con el otro, que es "
        "la forma que toma casi cualquier pregunta interesante del corte.") + f"""
      <p>Seis preguntas, y ninguna sale de un solo módulo. Cuatro empiezan en el capítulo 4 y se
        contestan con lo que dice el 5: la pregunta que el 4 dejó abierta sobre las sedes de
        Bogotá —si su exceso de parejas es atracción o intensidad variable—, una misma expresión
        que nombra dos operaciones distintas, dos bandas de simulación que se parecen y no
        contrastan lo mismo, y dos maneras de fijar la escala: el cuadrante y el ancho de banda.
        La quinta cruza el 5 con el capítulo 1: a cuántas sedes independientes equivalen las de
        Bogotá cuando vienen en grupos. La sexta recorre los dos capítulos a la vez: cómo entra la
        ventana en cada estimador.</p>

      <p>Si un bloque de este preparcial se parece al parcial, es este. No porque sea más
        difícil, sino porque un examen de corte pregunta por el corte y no por el capítulo, y
        estudiar capítulo a capítulo prepara mal para eso.</p>

{bloque_quiz("bloque-c", "Bloque C · los capítulos 4 y 5 a la vez",
             "Seis preguntas de los cuatro tipos. Las numéricas aceptan coma o punto decimal, "
             "y la tolerancia va dicha en el enunciado. El enlace de repaso del recuento final "
             "apunta al módulo del capítulo 5 por el que conviene empezar; desde ahí, el "
             "capítulo remite al 4.")}
      <p>Con esto queda recorrido el temario. Lo que sigue lo aplica entero, de la ventana al
        modelo, sobre un patrón nuevo.</p>
{CIERRE}"""


# =====================================================================
# MÓDULO · Las seis rutinas
#
# Cada bloque se EJECUTÓ para escribir su `#>`, y `verifica_bloques.py` los
# vuelve a ejecutar encadenados y contrasta cada cifra anunciada. Los seis
# son autónomos —cargan sus paquetes y sus datos— porque el preparcial se
# lee por partes. El código se escribe tal cual y se escapa al montar la
# pestaña: escribir «&lt;-» a mano en un bloque es la forma de que un día
# alguien copie «&lt;-» a su consola.
#
# Y las dos pestañas de cada rutina llevan comentarios parejos: el Corte I
# encontró catorce comentarios en R contra seis en Python, con dos rutinas
# que en Python solo calculaban (§12.7, «contar los comentarios»).
# =====================================================================
import html as _html


def tabs(etiqueta, r_code, py_code):
    r_code, py_code = _html.escape(r_code, quote=False), _html.escape(py_code, quote=False)
    return f"""      <div class="code-tabs">
        <div class="code-tabs-nav" role="tablist" aria-label="{etiqueta}">
          <button class="code-tab-btn active" data-lang="r" role="tab" aria-selected="true">R</button>
          <button class="code-tab-btn" data-lang="python" role="tab" aria-selected="false">Python</button>
        </div>
        <div class="code-tab-panel" data-lang="r">
          <pre><code class="language-r">{r_code}</code></pre>
        </div>
        <div class="code-tab-panel" data-lang="python" hidden>
          <pre><code class="language-python">{py_code}</code></pre>
        </div>
      </div>
"""


R_1 = '''library(sf)
library(spatstat)
cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
urb  <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)

# Antes de nada: los dos en el mismo sistema de referencia
st_crs(cole) == st_crs(urb)
#> [1] TRUE

# La ventana se declara: es la región donde se buscó, no el marco del dibujo
W  <- as.owin(st_geometry(st_union(urb)))
xy <- st_coordinates(cole)
p  <- ppp(xy[, 1], xy[, 2], window = W)   # avisa dos veces: puntos fuera y repetidos
c(dentro = npoints(p), fuera = npoints(attr(p, "rejects")))
#> dentro  fuera
#>   2107    102

# La comprobación: los de dentro y los descartados, contados cada uno por su
# lado, suman las filas del archivo
npoints(p) + npoints(attr(p, "rejects")) == nrow(cole)
#> [1] TRUE

# Y el segundo aviso de ppp(), que tampoco se lee: sedes en el mismo sitio
sum(duplicated(p))
#> [1] 40

# La intensidad, en la unidad que se publica: el CRS mide en metros
round(intensity(p) * 1e6, 4)   # sedes por km2
#> [1] 5.6932'''

PY_1 = '''import geopandas as gpd
cole = gpd.read_file("datos/procesado/bogota_colegios.gpkg")
urb = gpd.read_file("datos/procesado/bogota_ventana_urbana.gpkg")

# Antes de nada: los dos en el mismo sistema de referencia
print(cole.crs.to_epsg() == urb.crs.to_epsg())
#> True

# La ventana se declara; aquí no hay ppp(), así que el descarte se hace a mano.
# `covered_by` y no `within`: within dejaría fuera un punto sobre el borde, y
# ppp() lo deja dentro (union_all pide geopandas 1.0 o posterior)
W = urb.geometry.union_all()
dentro = cole.geometry.covered_by(W).to_numpy()

# La comprobación: los de dentro y los de fuera, contados por separado
print(int(dentro.sum()), int((~dentro).sum()))
#> 2107 102

# Y las sedes que repiten las coordenadas de otra, que ppp() avisa
print(int(cole.geometry[dentro].duplicated().sum()))
#> 40

# La intensidad, en la unidad que se publica: el CRS mide en metros
print(round(dentro.sum() / (W.area / 1e6), 4))   # sedes por km2
#> 5.6932'''

R_2 = '''library(sf)
library(spatstat)
cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
urb  <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
p  <- ppp(xy[, 1], xy[, 2], window = as.owin(st_geometry(st_union(urb))))

qt <- quadrat.test(p, nx = 5, ny = 5)

# El supuesto ANTES que el p-valor: ninguna celda puede esperar menos de 5
round(min(qt$expected), 2)
#> [1] 5.84

# Y solo entonces el estadístico, con sus grados de libertad
c(chi2 = round(unname(qt$statistic), 2), gl = unname(qt$parameter))
#>   chi2     gl
#> 204.75  18.00
signif(qt$p.value, 3)
#> [1] 2.25e-33'''

PY_2 = '''import geopandas as gpd, numpy as np
from shapely.geometry import box
cole = gpd.read_file("datos/procesado/bogota_colegios.gpkg")
W = gpd.read_file("datos/procesado/bogota_ventana_urbana.gpkg").geometry.union_all()
dentro = cole.geometry.covered_by(W).to_numpy()   # como en la rutina 1
px, py = cole.geometry.x.to_numpy()[dentro], cole.geometry.y.to_numpy()[dentro]

# La rejilla parte el rectángulo que encierra la ventana, y el binado es el
# de quadratcount: cada celda abierta por la izquierda y cerrada por la derecha
k = 5
x0, y0, x1, y1 = W.bounds
xs, ys = np.linspace(x0, x1, k + 1), np.linspace(y0, y1, k + 1)
ix = np.clip(np.searchsorted(xs, px, "left") - 1, 0, k - 1)
iy = np.clip(np.searchsorted(ys, py, "left") - 1, 0, k - 1)

# La esperanza de cada celda es λ por su área RECORTADA contra la ventana
lam = len(px) / W.area
O, E = [], []
for i in range(k):
    for j in range(k):
        a = box(xs[i], ys[j], xs[i + 1], ys[j + 1]).intersection(W).area
        if a > 0:
            O.append(int(((ix == i) & (iy == j)).sum()))
            E.append(lam * a)
O, E = np.array(O), np.array(E)

# El supuesto ANTES que el estadístico
print(round(E.min(), 2))
#> 5.84
print(round(((O - E) ** 2 / E).sum(), 2), len(O) - 1)
#> 204.75 18'''

R_3 = '''library(spatstat)
set.seed(2026)
e <- envelope(redwood, Lest, nsim = 39, correction = "translate",
              savefuns = TRUE, verbose = FALSE)

# Lo que se pidió, leído del propio objeto y no de la memoria
c(nsim = attr(e, "einfo")$nsim, nrank = attr(e, "einfo")$nrank)
#>  nsim nrank
#>    39     1

# El nivel PUNTUAL de esta banda: 2 * nrank / (nsim + 1)
2 * attr(e, "einfo")$nrank / (attr(e, "einfo")$nsim + 1)
#> [1] 0.05

# El test global de la curva entera, con las MISMAS simulaciones...
dclf.test(e)$p.value
#> [1] 0.025

# ... sobre un tramo de r que también se declara: aquí, el de por defecto
range(e$r)
#> [1] 0.00 0.25

# ... y la comprobación: no puede bajar de 1 / (nsim + 1), y aquí cae justo ahí
dclf.test(e)$p.value == 1 / (attr(e, "einfo")$nsim + 1)
#> [1] TRUE

# Un valor de la curva observada, para cotejarlo con la otra pestaña
round(Lest(redwood, correction = "translate", r = c(0, 0.05, 0.11))$trans[3], 5)
#> [1] 0.16196'''

PY_3 = '''import numpy as np, pandas as pd
reg = pd.read_csv("precalculo/salidas/cap4_regimenes.csv")
rw = reg.loc[reg.patron == "redwood", ["x", "y"]].to_numpy()   # ventana [0,1] x [-1,0]
n = len(rw)

# Python no simula las mismas 39: no comparte generador con R. Lo que se
# reproduce es la curva observada, y la aritmética del nivel y del p mínimo
dx = np.abs(rw[:, None, 0] - rw[None, :, 0])
dy = np.abs(rw[:, None, 1] - rw[None, :, 1])
d = np.hypot(dx, dy)
np.fill_diagonal(d, np.inf)

# El peso de traslación en un cuadrado de lado 1: |W| / |W ∩ (W + v)|
peso = 1 / ((1 - dx) * (1 - dy))
K = peso[d <= 0.11].sum() / (n * (n - 1))
print(round(float(np.sqrt(K / np.pi)), 5))
#> 0.16196

# Se coteja en 0.11 y no en 0.1 a propósito: hay parejas EXACTAMENTE a 0.1
# (casi todas las coordenadas van en pasos de 0.02), y si Kest las cuenta o
# no depende del redondeo de cada distancia y de la rejilla de r que se le
# pida. En un radio sin empates no hay nada que discrepar
print(int((np.abs(d - 0.1) < 1e-9).sum()))
#> 32
print(2 * 1 / (39 + 1), 1 / (39 + 1))   # nivel puntual y p mínimo
#> 0.05 0.025'''

R_4 = '''library(spatstat)

# El selector devuelve un número, y el aviso se queda en la consola
s <- bw.ppl(japanesepines)
h <- attr(s, "h")                        # el intervalo en que buscó
c(sigma = round(as.numeric(s), 4), tope = round(max(h), 4))
#>  sigma   tope
#> 0.7071 0.7071

# La comprobación que el número no hace por sí solo
as.numeric(s) == max(h)
#> [1] TRUE

# La masa: integrar la superficie y compararla con n
masa <- function(...) integral(density(japanesepines, sigma = 0.1, ...))
round(c(sin_corregir = masa(edge = FALSE), defecto = masa(),
        diggle = masa(diggle = TRUE)), 3)
#> sin_corregir      defecto       diggle
#>       53.082       63.998       65.000
npoints(japanesepines)
#> [1] 65'''

PY_4 = '''import numpy as np, pandas as pd
from scipy.stats import norm
reg = pd.read_csv("precalculo/salidas/cap4_regimenes.csv")
jp = reg.loc[reg.patron == "japanesepines", ["x", "y"]].to_numpy()   # ventana [0,1]^2

# El tope de bw.ppl es la mitad del diámetro de la ventana: el diámetro de un
# cuadrado es su diagonal, √2, y el tope es su mitad
print(round(float(np.hypot(1, 1) / 2), 4))
#> 0.7071

# Sin corregir, la integral es la suma de la masa que cada núcleo deja DENTRO.
# En un rectángulo esa fracción tiene fórmula cerrada, eje por eje
s = 0.1
e = ((norm.cdf((1 - jp[:, 0]) / s) - norm.cdf(-jp[:, 0] / s))
     * (norm.cdf((1 - jp[:, 1]) / s) - norm.cdf(-jp[:, 1] / s)))

# La comprobación: la suma frente a n, y la fracción que conserva el pino
# que más masa pierde
print(round(float(e.sum()), 3), len(jp), round(float(e.min()), 3))
#> 53.159 65 0.336

# La corrección por defecto divide, en cada píxel, por la masa del núcleo
# centrado AHÍ, no en cada pino: por eso no conserva n
m = 128
c = (np.arange(m) + 0.5) / m
U, V = np.meshgrid(c, c)
eu = ((norm.cdf((1 - U) / s) - norm.cdf(-U / s))
      * (norm.cdf((1 - V) / s) - norm.cdf(-V / s)))
dens = sum(norm.pdf(U, x, s) * norm.pdf(V, y, s) for x, y in jp)
print(round(float((dens / eu).mean()), 3), len(jp))
#> 64.075 65'''

R_5 = '''library(sf)
library(spatstat)
cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
urb  <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
p  <- ppp(xy[, 1], xy[, 2], window = as.owin(st_geometry(st_union(urb))))

# Coordenadas centradas y en kilómetros: el mismo modelo, legible
X0 <- mean(p$x); Y0 <- mean(p$y)
covs <- list(xc = function(x, y) (x - X0) / 1000,
             yc = function(x, y) (y - Y0) / 1000)
f  <- ppm(p ~ xc + yc, covariates = covs)
ee <- sqrt(diag(vcov(f)))

# La comprobación: un error estándar por coeficiente, no una matriz vacía
length(ee) == length(coef(f))
#> [1] TRUE
round(coef(f) / ee, 2)
#> (Intercept)          xc          yc
#>     -553.73       -4.82       -1.70

# El mismo modelo con las coordenadas crudas: ajusta, vcov() avisa y devuelve
# NULL, y la misma comprobación lo caza sin que nada se detenga
f_crudo <- ppm(p ~ x + y)
length(sqrt(diag(vcov(f_crudo)))) == length(coef(f_crudo))
#> [1] FALSE'''

PY_5 = '''import numpy as np, pandas as pd
urb = pd.read_csv("precalculo/salidas/cap5_bogota_urbana.csv")

# La matriz de diseño cruda —una columna de unos y dos de siete cifras— y la
# misma con las coordenadas centradas y en kilómetros
X = np.column_stack([np.ones(len(urb)), urb.x, urb.y])
Xc = np.column_stack([np.ones(len(urb)), (urb.x - urb.x.mean()) / 1000,
                      (urb.y - urb.y.mean()) / 1000])

# El número de condición recíproco de la matriz de diseño, cruda y centrada
print(f"{1 / np.linalg.cond(X):.3e}", f"{1 / np.linalg.cond(Xc):.4f}")
#> 1.698e-10 0.1224

# La comprobación: lo que ppm invierte es del tipo X'X, y su condición es la
# de X al cuadrado. Por debajo del épsilon de la máquina, la inversa no existe
print(f"{1 / np.linalg.cond(X.T @ X):.3e}", f"{1 / np.linalg.cond(Xc.T @ Xc):.4f}",
      f"{np.finfo(float).eps:.3e}")
#> 2.883e-20 0.0150 2.220e-16'''

R_6 = '''library(spatstat)
# Por defecto la corrección la elige kppm, y no la anota entre sus argumentos…
k_def <- kppm(redwood ~ 1, "Thomas")
is.null(k_def$Fit$statargs$correction)
#> [1] TRUE
# …solo se adivina por el nombre de la columna de la K que guarda dentro
fvnames(k_def$Fit$Stat, ".y")
#> [1] "iso"

k_iso <- kppm(redwood ~ 1, "Thomas", statargs = list(correction = "isotropic"))
k_tr  <- kppm(redwood ~ 1, "Thomas", statargs = list(correction = "translate"))

# La comprobación: escrita en la llamada, la corrección viaja dentro del
# ajuste y se lee de vuelta en el objeto que se publica
c(iso = k_iso$Fit$statargs$correction, trans = k_tr$Fit$statargs$correction)
#>         iso       trans
#> "isotropic" "translate"

# Y no da lo mismo: el contraste mínimo ajusta a una ESTIMACIÓN de K
round(rbind(iso = unlist(parameters(k_iso)),
            trans = unlist(parameters(k_tr)))[, c("kappa", "scale")], 4)
#>         kappa  scale
#> iso   23.5486 0.0471
#> trans 18.9885 0.0500
# mu: plántulas por conglomerado
round(c(iso = k_iso$mu, trans = k_tr$mu), 3)
#>   iso trans
#> 2.633 3.265'''

PY_6 = '''import json, numpy as np
sol = json.load(open("precalculo/salidas/cap5_soluciones.json"))["e5"]["solucion"]

# Python no ajusta kppm. Lee los dos juegos de parámetros que R dejó escritos
# y evalúa con ellos la K teórica de Thomas, que tiene fórmula cerrada
def K_thomas(r, kappa, escala):
    return np.pi * r ** 2 + (1 - np.exp(-r ** 2 / (4 * escala ** 2))) / kappa

# La comprobación: cuánto se separan las dos curvas donde están los grumos
for r in (0.05, 0.1):
    a = K_thomas(r, sol["isotropica"]["kappa"], sol["isotropica"]["escala"])
    b = K_thomas(r, sol["traslacion"]["kappa"], sol["traslacion"]["escala"])
    print(r, round(a, 5), round(b, 5), round(100 * abs(a - b) / a, 2))
#> 0.05 0.0183 0.0195 6.55
#> 0.1 0.06015 0.0647 7.55'''


def mod_rutinas(num):
    return cabecera(
        num, "Seis rutinas que el parcial puede pedir", "Six routines",
        "Escribir, leer o corregir las seis operaciones que más aparecen en los dos capítulos, "
        "y saber con qué línea se comprueba cada una.") + """
      <p>No hay nada que responder en este módulo. Son seis procedimientos con la salida
        <strong>que devuelven de verdad</strong>: se escribieron ejecutándolos, y un guion los
        vuelve a ejecutar y comprueba que cada salida —las líneas que empiezan por
        <code>#&gt;</code>— siga cuadrando. La pestaña de R hace el procedimiento entero. La de
        Python lo hace en las dos primeras rutinas; en las otras cuatro, donde
        <code>spatstat</code> no tiene equivalente, reproduce la parte que no es aleatoria o
        comprueba lo mismo por otro camino, y el párrafo de debajo de cada una dice cuál. Se
        corren desde la carpeta del curso, con las rutas de datos del repositorio, como los
        capítulos.</p>

      <p>Los seis comparten una forma, y esa forma es lo que hay que llevarse: cada uno tiene
        <strong>una línea que comprueba</strong> que el resultado es el que se cree. Es la defensa
        contra lo que adelantó el bloque B: en estos dos capítulos casi nada falla con un mensaje
        de error, y un número con aspecto normal puede ser un tope, una masa que no cuadra o un
        ajuste sin errores estándar.</p>

      <h3>1 · Del archivo al patrón, con la ventana declarada</h3>
      <p>El primer paso de todo, y el que decide la intensidad antes de calcularla: qué región se
        declara como el sitio donde se buscó, y qué puntos quedan fuera. <code>ppp()</code> los
        descarta con un aviso que nadie lee, y con otro avisa de las sedes repetidas; la
        comprobación es contar las dos cosas.</p>

""" + tabs("Del archivo al patrón", R_1, PY_1) + """
      <p>La λ sale en sedes por metro cuadrado, porque el sistema de referencia mide en metros, y
        el <code>* 1e6</code> la pasa a sedes por kilómetro cuadrado. Las dos pestañas cuentan los
        mismos puntos dentro y fuera, por caminos distintos: <code>ppp()</code> en R y una prueba
        de pertenencia geométrica en Python.</p>
""" + f"""
      <p>Las {c('c4m1_fuera_urb')} que quedan fuera del perímetro urbano no son todas del resto del
        Distrito: {cn('resto_dc.n_resto')} caen en él y {c('c4m1_fuera_dc')}, fuera también del
        Distrito. Por eso el archivo tiene {c('c4m1_total')} filas, y el D.C. de la primera
        pregunta del bloque A, {c('c4m1_n_dc')} sedes.</p>

      <h3>2 · El test de cuadrantes, con su supuesto antes que su p-valor</h3>
      <p>El χ² y su p-valor salen siempre; lo que no dicen por sí solos es si vale la aproximación
        de la que sale ese p-valor. La comprobación es la menor esperanza entre las celdas
        —ninguna debería esperar menos de 5 puntos—, y se mira antes.</p>

""" + tabs("El test de cuadrantes con su supuesto", R_2, PY_2) + """
      <p>La pestaña de Python rehace el χ² entero, y para que cuadre hay que reproducir dos
        convenios: el binado —qué celda se queda un punto que cae justo en una línea— y la
        esperanza de cada celda, que es la intensidad por su área recortada contra la ventana, no
        por el área entera de la celda.</p>

      <h3>3 · Envolvente y test global, con el número de simulaciones declarado</h3>
      <p>Sobre las plántulas de secuoya (<code>redwood</code>). La banda es puntual: su nivel,
        2·nrank/(nsim + 1), vale para cada r por separado, no para la curva entera. El test
        global —aquí el DCLF, <code>dclf.test</code>, que contrasta la curva entera sobre un tramo
        de r que también se declara— reutiliza las mismas simulaciones, y su p-valor no puede bajar
        de 1/(nsim + 1). Cuando cae justo ahí, como en esta rutina, lo que dice es que ninguna
        simulación se alejó tanto como el dato: es una cota superior, no una medida.</p>

""" + tabs("Envolvente y test global", R_3, PY_3) + """
      <p>Python no puede reproducir las simulaciones —no comparte generador con R—, así que
        reproduce lo que no es aleatorio: la curva observada y la aritmética del nivel. Y al
        hacerlo destapa una trampa que la ayuda de <code>Kest</code> no menciona, y que
        <code>Lest</code>, que la llama por dentro, hereda: cuando hay parejas justo a la distancia
        que se pide, <code>Kest</code> cuenta unas y otras no, según el redondeo de cada distancia y
        hasta según la rejilla de r que se le pida. Por eso se coteja en un radio sin empates.</p>

      <h3>4 · El ancho, la pared y la masa</h3>
      <p>Sobre los pinos japoneses (<code>japanesepines</code>). Dos cosas que el número no dice
        por sí solo: si el selector devolvió el extremo de su intervalo —la «pared» del capítulo
        5— y si la superficie integra el número de puntos.</p>

""" + tabs("El ancho, la pared y la masa", R_4, PY_4) + """
      <p>Fíjate en la segunda de las tres masas. Con las sedes de Kennedy del capítulo 5, la
        corrección por defecto se pasa de n; con estos pinos <strong>se queda corta</strong>. No
        hay una ley. Esa corrección divide la estimación de cada sitio del mapa por la fracción del
        núcleo centrado en ese sitio que cae dentro de la ventana, y el total sale por encima o por
        debajo de n según a qué distancia del borde estén los puntos. La de Diggle divide en otro
        sitio: el núcleo de cada punto, por la fracción de ese mismo núcleo que cae dentro. Así cada
        punto aporta exactamente 1, y por eso es la única que integra n siempre. Las dos pestañas
        llegan a las masas por caminos distintos —R suma una rejilla de píxeles, Python integra la
        fórmula exacta sin corregir y una rejilla propia con la corrección por defecto— y,
        redondeadas al entero, coinciden, que es lo que la comparación con n necesita.</p>

      <h3>5 · Un <code>ppm</code> que se puede leer</h3>
      <p>Ajustar es una línea; leer lo ajustado exige comprobar antes que haya un error estándar
        por coeficiente. Con coordenadas de siete cifras no lo hay, y nada se detiene:
        <code>vcov()</code> avisa y devuelve <code>NULL</code>.</p>

""" + tabs("Un ppm que se puede leer", R_5, PY_5) + """
      <p>Las dos pestañas miran el mismo problema desde sitios distintos. R ajusta el modelo
        centrado y el crudo, y la misma línea separa el que se puede leer del que no. Python, antes
        de que haya modelo, mide el número de condición de la matriz de diseño con las coordenadas
        crudas y con las centradas, y el de la matriz que el ajuste tendría que invertir: el
        problema está en la escala de los números, no en la verosimilitud. El capítulo 5 publica una
        cifra parecida calculada en R sobre la matriz de la cuadratura, con las sedes y los puntos
        ficticios; Python la calcula sobre las sedes solas, y por eso no coinciden, aunque caen en
        el mismo orden de magnitud, que es lo que importa.</p>

      <h3>6 · <code>kppm</code> con la corrección escrita</h3>
      <p>Sobre las plántulas de secuoya. Un ajuste de conglomerado depende de con qué estimación de
        K se hizo, porque <code>kppm</code> ajusta por contraste mínimo: busca los parámetros cuya K
        teórica más se parece a una K estimada del patrón. La llamada por defecto elige esa
        estimación sin decirlo: no la anota entre sus argumentos, y solo se adivina por el nombre
        de la columna de la K que guarda. La comprobación es escribirla en la llamada y leerla de
        vuelta en el objeto que se publica.</p>

""" + tabs("kppm con la corrección escrita", R_6, PY_6) + """
      <p>Las curvas teóricas de los dos ajustes se separan bastante menos de lo que cambian κ y
        las plántulas por conglomerado: el contraste mínimo busca en un valle casi plano, y por eso
        cambiar el estimador de K mueve tanto el sitio del mínimo. Son dos descripciones distintas
        del mismo dato, y ninguna es «la» correcta: lo obligatorio es escribir cuál se usó.</p>

      <p>El bloque que viene no se responde con un módulo suelto: cruza los dos capítulos.</p>
""" + CIERRE


# =====================================================================
# MÓDULO · Los cinco ejercicios sobre el oro de Murchison
#
# El marcado de la CASA, no uno inventado: `cuenta_sitio.py` cuenta los
# ejercicios por `.ejercicio-guiado` y el desplegable se cablea por
# `.ejercicio-boton`. Cada respuesta llega anclada a un trozo literal de su
# enunciado, que se pinta como su encabezado; si el ancla no estuviera en el
# enunciado, la respuesta contestaría a una pregunta que nadie ve.
# =====================================================================
def _codigo(texto):
    """Las comillas invertidas pasan a <code>, y su contenido se ESCAPA:
    `D <- distfun(fallas)` llevaba un «<» crudo dentro del HTML, que el
    navegador perdona y un extractor de texto se come entero."""
    return re.sub(r"`([^`]+)`", lambda m: "<code>" + _html.escape(m.group(1), quote=False) + "</code>",
                  texto)


def _pregunta(pide):
    i = 1 if pide.startswith("¿") else 0
    t = pide[:i] + pide[i].upper() + pide[i + 1:]
    if i and not t.endswith("?"):
        return t + "?"
    return t if t[-1] in ".?!" else t + "."


def _valor(v):
    """Un paso de la solución, como se lee: entero con separador de millar, o
    seis cifras significativas. Es presentación de un número que ya viene
    calculado en R."""
    if isinstance(v, bool):
        return "sí" if v else "no"
    if float(v) == int(float(v)) and abs(float(v)) < 1e15:
        return ent(v)
    t = f"{float(v):.6g}"
    # Por encima de mil, el separador de millar de la casa (U+202F), que
    # «132497» sin él se lee mal; la notación científica se deja como está.
    if abs(float(v)) >= 1000 and "e" not in t:
        entero, _, frac = t.partition(".")
        signo = "-" if entero.startswith("-") else ""
        entero = f"{int(entero.lstrip('-')):,}".replace(",", "\u202f")
        t = signo + entero + ("." + frac if frac else "")
    return t


def ejercicio(k, e):
    pasos = "".join(
        f'                <tr><th scope="row">{p["paso"]}</th><td>{_valor(p["valor"])}</td></tr>\n'
        for p in e["pasos"])
    extra = ""
    cuad = e["solucion"].get("cuadrantes")
    if cuad:
        filas = "".join(
            f'                <tr><th scope="row">{ej(z["k"])}</th><td>{n(z["chi2"], 2)}</td>'
            f'<td>{ent(z["gl"])}</td><td>{z["p"]:.3g}</td><td>{n(z["esperanza_min"], 2)}</td></tr>\n'
            for z in cuad)
        extra = f"""            <div class="tabla-scroll">
            <table>
              <caption>El test de cuadrantes sobre el rectángulo, rejilla por rejilla.</caption>
              <thead><tr><th scope="col">Rejilla</th><th scope="col">χ²</th><th scope="col">gl</th>
                <th scope="col">p-valor</th><th scope="col">Esperanza mínima</th></tr></thead>
              <tbody>
{filas}              </tbody>
            </table>
            </div>
"""
    resp = e["solucion"]["respuestas"]
    for r in resp:
        if r["pide"] not in e["enunciado"]:
            sys.exit(f"PARADO: una respuesta del ejercicio {k} contesta a «{r['pide']}», "
                     "que su enunciado no pregunta")
    respuestas = "".join(
        f'            <p class="ejercicio-respuesta"><strong>{_codigo(_pregunta(r["pide"]))}</strong>\n'
        f'              {_codigo(r["respuesta"])}</p>\n'
        for r in resp)
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}{'' if e['titulo'][-1] in '.?!' else '.'}</strong>
            {_codigo(e['enunciado'])}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="pre2-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="pre2-e{k}-sol" hidden>
            <div class="tabla-scroll">
            <table>
              <caption>Los pasos de la solución, calculados en R.</caption>
              <thead><tr><th scope="col">Paso</th><th scope="col">Valor</th></tr></thead>
              <tbody>
{pasos}              </tbody>
            </table>
            </div>
{extra}{respuestas}            <p class="ejercicio-lectura">{_codigo(e['solucion']['lectura'])}</p>
          </div>
        </div>
"""


def mod_ejercicios(num):
    claves = sorted(EJ, key=lambda x: int(x[1:]))
    cuerpos = "".join(ejercicio(i + 1, EJ[k]) for i, k in enumerate(claves))
    mapa = "".join(
        f'          <li><strong>{EJ[k]["titulo"]}</strong> — '
        + ", ".join(f'{m.split(".")[0][:3]}. {m.split(".")[0][3]} · módulo {m.split(".m")[1]}'
                    for m in EJ[k]["modulos"]) + "</li>\n"
        for k in claves)
    return cabecera(
        num, "Cinco ejercicios sobre el oro de Murchison", "Five exercises on Murchison gold",
        "Recorrer un patrón entero, desde la elección de la ventana hasta el modelo ajustado, "
        "tomando y declarando cada una de las decisiones que los dos capítulos enseñan a tomar.") + f"""
      <p>Hasta aquí has reconocido decisiones ajenas. Aquí las tomas tú, sobre un patrón que
        ningún documento del curso ha usado: los <strong>yacimientos de oro de Murchison</strong>,
        en Australia Occidental. Los trae <code>spatstat.data</code>, junto con dos capas más: las
        <strong>fallas geológicas</strong>, guardadas como segmentos, y el afloramiento de
        <em>greenstone</em> (roca verde, la que alberga el oro), guardado como un polígono
        <code>owin</code>, el mismo tipo de objeto que una ventana. Se cargan con
        <code>data(murchison)</code>.</p>

      <p>Los cinco van en orden: el 1 deja el cociente que el 4 coteja con un coeficiente, el 4
        deja las covariables y la cuadratura que usa el 5, y el 2 y el 3 son el mismo problema —el
        borde— visto en K y en la intensidad. Es el recorrido entero de un proyecto de patrones
        puntuales, en miniatura. Y sobre este patrón casi todas las trampas de los dos capítulos
        vuelven a aparecer, algunas con el resultado al revés que en Bogotá: no sirve recordar el
        veredicto de los capítulos, hay que volver a medirlo.</p>

      <div class="tip-box">
        <h3>Qué módulos toca cada uno</h3>
        <ol class="lista-literales" type="1">
{mapa}        </ol>
        <p style="margin-bottom:0;">Las soluciones están calculadas en R y plegadas debajo de cada
          enunciado, tras el botón «Solución». Dentro, cada pregunta del enunciado reaparece como
          encabezado, con su respuesta debajo. Contesta el ejercicio entero antes de
          desplegarla.</p>
      </div>
{cuerpos}
      <p>Si los cinco te salieron, recorriste lo que el corte enseña, de la ventana al modelo. Lo
        que queda es el catálogo de los errores que se repiten, por si prefieres repasar por error y
        no por temario.</p>
{CIERRE}"""


# =====================================================================
# MÓDULO · Qué entra en el parcial, y qué no
# =====================================================================
def mod_alcance(num):
    bloques = []
    for doc in ("cap4", "cap5"):
        filas = [f for f in ALC.ALCANCE if f["doc"] == doc]
        renglones = "\n".join(
            "          <li>" + enlace_modulo(doc, f["modulo"], f"Módulo {ent(f['modulo'])} · {f['titulo']}")
            + "</li>" for f in filas)
        bloques.append(f"""      <h3>{NOMBRE_CAP[doc]}</h3>
        <p>Entran sus {ent(len(filas))} módulos de contenido; los dos de práctica quedan fuera, y
          abajo se dice por qué.</p>
        <ol class="lista-literales" type="1">
{renglones}
        </ol>""")
    fuera = "\n".join(
        f'          <li><strong>{NOMBRE_CAP[f["doc"]].split(" · ")[0]} · módulo {f["modulo"]} · '
        f'{f["titulo"]}</strong></li>'
        for f in ALC.FUERA_DE_ALCANCE)
    return cabecera(
        num, "Qué entra en el parcial, y qué no", "What is on the exam",
        "Nada todavía. Este módulo dice qué se evalúa, qué no, y cómo leer lo que viene "
        "después.") + f"""
      <p>El parcial del Corte II es el <strong>{fecha_larga(meta['fecha_parcial'])}</strong>. Este
        preparcial no tiene nota, puedes repetirlo tantas veces como quieras y no se envía a
        ninguna parte: existe para que llegues al parcial sabiendo <em>qué</em> sabes, que no es lo
        mismo que haber leído los capítulos. Y no es el parcial: sus preguntas no son las del
        examen.</p>

      <p>En el parcial no se evalúa recordar cifras. Se evalúan cuatro cosas, y se puede fallar en
        una sin fallar en las otras:</p>
      <ul class="lista-literales">
        <li><strong>el procedimiento</strong>: qué se calcula y con qué línea se comprueba;</li>
        <li><strong>el concepto</strong>: qué significa un resultado y, sobre todo, qué
          <em>no</em> significa;</li>
        <li><strong>la lectura</strong>: qué dice una curva o una banda, y qué no se puede concluir
          de ella;</li>
        <li><strong>la decisión</strong>: qué ventana, qué ancho de banda, qué corrección y qué
          modelo se usan, y cómo se declara cada uno.</li>
      </ul>
      <p>Esta página entrena las cuatro: los bloques de preguntas, el concepto y la lectura; las
        rutinas, el procedimiento; los ejercicios, la decisión.</p>

      <div class="definition">
        <h3>Cómo funciona</h3>
        <p>La página tiene siete módulos y se recorre en este orden: este, que dice qué entra; los
          bloques A y B, once preguntas por capítulo; seis rutinas de código en R y Python, cada una
          con la línea que la comprueba; el bloque C, seis preguntas que cruzan los dos capítulos;
          cinco ejercicios guiados sobre un patrón nuevo, los yacimientos de oro de Murchison; y el
          catálogo de los quince errores que más se repiten.</p>
        <p>Las preguntas son de cuatro tipos: opción múltiple, varias respuestas, respuesta
          numérica y lectura de gráfico. Al fallar por primera vez sale una
          <strong>pista</strong> y se puede reintentar; al segundo fallo se revela la respuesta. En
          las de varias respuestas, además, te dice cuántas de las que marcaste están bien y cuántas
          te faltan.</p>
        <p style="margin-bottom:0;">Y <strong>todas</strong> las opciones llevan explicación,
          también las incorrectas: dicen a qué error lleva el razonamiento que conduce a ellas y,
          cuando ese error produce una cifra, cuál es. Leerlas cuando aciertas también sirve, porque
          acertar por el motivo equivocado es lo que un parcial se encarga de descubrir.</p>
      </div>

      <h3>El temario que entra</h3>
      <p>Entran <strong>{ent(meta['n_modulos_alcance'])} módulos</strong>, los once de contenido de
        cada capítulo. Cada uno tiene al menos una pregunta en este preparcial, y ninguna pregunta
        del preparcial sale de fuera de ellos.</p>

{"".join(b + chr(10) for b in bloques)}
      <div class="warning">
        <h3>Lo que NO entra</h3>
        <p>De cada capítulo quedan fuera los dos últimos módulos —la autoevaluación con sus
          ejercicios y el simulacro del quiz—, porque no añaden temario: son práctica sobre los once
          anteriores, y como práctica siguen sirviendo.</p>
        <ol class="lista-literales" type="1">
{fuera}
        </ol>
        <p style="margin-bottom:0;">Los capítulos 1 a 3 no entran por sí mismos. Aparecen solo
          donde el 4 y el 5 se apoyan en ellos —la ventana como decisión, el MAUP (el problema de
          la unidad de área modificable) en el tamaño de la celda, el efecto de diseño en los
          errores de un ajuste—, y se preguntan desde ese módulo.</p>
      </div>

      <p>El último módulo reúne los quince errores que más se repiten en estos dos capítulos, cada
        uno con las cifras que lo miden y el módulo al que conviene volver. Déjalo para el final:
        varias de sus cifras contestan preguntas de los bloques, y leerlo antes convierte el
        diagnóstico en un ejercicio de memoria. Sigue con el bloque A.</p>
{CIERRE}"""


# =====================================================================
# MÓDULO · Los errores que se repiten
# =====================================================================
def mod_errores(num):
    tarjetas = []
    for e in ERRORES:
        titulo_mod = _titulo_modulo(e["doc"], e["modulo"])
        renglones = [f'            <li>{cifra(k)} — {que(k)}</li>' for k in e["claves"]]
        for nv in e.get("nuevas", []):
            renglones.append(f'            <li>{cifra(nv["ruta"], val_nuevo(nv["ruta"]))} — {nv["que"]}</li>')
        medidas = "\n".join(renglones)
        volver = enlace_modulo(e["doc"], e["modulo"],
                               f"cap. {e['doc'][3]} · módulo {e['modulo']} — {titulo_mod}")
        tarjetas.append(f"""      <div class="tip-box">
        <h3>{e['titulo']}</h3>
        <p>{e['dice'][0].upper() + e['dice'][1:]}.</p>
        <p style="margin-bottom:0.5rem;"><strong>Lo que lo mide:</strong></p>
          <ul class="lista-literales">
{medidas}
          </ul>
        <p style="margin-bottom:0;"><strong>Adónde volver:</strong> {volver}.</p>
      </div>""")

    filas_repaso = "\n".join(
        f'            <tr><th scope="row">cap. {f["doc"][3]}</th><td>Módulo {f["modulo"]}</td>'
        f'<td>{enlace_modulo(f["doc"], f["modulo"], f["titulo"])}</td></tr>'
        for f in ALC.ALCANCE)
    return cabecera(
        num, "Los quince errores que se repiten", "The fifteen that keep coming back",
        "Reconocer, en el enunciado de un problema, cuál de los quince está a punto de "
        "cometerse.") + f"""
      <p>Los quince de abajo tienen algo en común, y por eso están juntos: <strong>ninguno produce
        un mensaje de error</strong>. Es lo que adelantó el bloque B, ahora uno por uno: el código
        corre, la superficie sale, la banda se dibuja y el coeficiente sale con su z, o sin ella y
        con un aviso que nadie lee. Lo que falla es que la cifra no es la que se creía, o no dice
        lo que se cree que dice.</p>

      <p>Cada uno viene con las cifras que lo miden —calculadas, no citadas de memoria— y con el
        módulo al que volver si al leerlo no reconoces de qué se habla.</p>

{"".join(t + chr(10) for t in tarjetas)}
      <h3>La ruta de repaso completa</h3>
      <p>Los {ent(meta['n_modulos_alcance'])} módulos que entran, en orden, por si prefieres repasar
        por temario en vez de por error.</p>
      <div class="tabla-scroll">
        <table>
          <caption>Los módulos que evalúa el parcial del Corte II</caption>
          <thead>
            <tr><th scope="col">Capítulo</th><th scope="col">Módulo</th><th scope="col">Tema</th></tr>
          </thead>
          <tbody>
{filas_repaso}
          </tbody>
        </table>
      </div>

      <p>Con eso está todo. El {fecha_larga(meta['fecha_parcial'])} el parcial pide las cuatro cosas
        del primer módulo —procedimiento, concepto, lectura y decisión—, y cada una tiene aquí su
        sitio: las rutinas, los tres bloques de preguntas y los ejercicios.</p>
{CIERRE}"""


# =====================================================================
# El orden del documento: el número, la cabecera y la navegación salen de
# la posición.
# =====================================================================
CONSTRUCTORES = [
    (mod_alcance,     "Qué entra en el parcial", "8 min"),
    (mod_bloque_a,    "Bloque A · capítulo 4", "30 min"),
    (mod_bloque_b,    "Bloque B · capítulo 5", "30 min"),
    (mod_rutinas,     "Seis rutinas que el parcial puede pedir", "25 min"),
    (mod_bloque_c,    "Bloque C · los dos capítulos", "15 min"),
    (mod_ejercicios,  "Cinco ejercicios: el oro de Murchison", "150 min"),
    (mod_errores,     "Los quince errores que se repiten", "15 min"),
]

QUIZ_JS = ("""    // Los ejes de las preguntas de gráfico del preparcial, con título. Los
    // ayudantes de la plantilla no lo ponen, y una curva sin rótulo en los
    // ejes es un dibujo, no una lectura.
    function ejesPreparcial(tituloX, tituloY, y = {}) {
      return {
        x: { title: { display: true, text: tituloX, font: { family: 'Montserrat', size: 11 } },
             ticks: { font: { family: 'Montserrat', size: 11 }, maxTicksLimit: 8, maxRotation: 0 },
             grid: { display: false } },
        y: Object.assign({ title: { display: true, text: tituloY, font: { family: 'Montserrat', size: 11 } },
             ticks: { font: { family: 'Fira Code', size: 11 } },
             grid: { color: 'rgba(148, 163, 184, 0.2)' } }, y)
      };
    }

    // El eje logarítmico, rotulado solo en las potencias de diez y sin ceros
    // de relleno: el formateador de Chart.js escribía «100.000» (cien con tres
    // decimales), que con el punto decimal del material se lee como cien mil.
    function ejeLogPreparcial() {
      return { type: 'logarithmic',
               ticks: { font: { family: 'Fira Code', size: 11 },
                        callback: v => { const l = Math.log10(v);
                                         return Math.abs(l - Math.round(l)) < 1e-9 ? String(v) : ''; } } };
    }

    // ¿Es el gráfico del ancho de un teléfono? Se pregunta al gráfico ya
    // dibujado, no al lienzo antes de entrar en la página: la versión que
    // medía `canvas.clientWidth` lo leía siempre como 0 y dejaba la leyenda
    // en 10 px también en el escritorio (auditoría de gráficos, ronda 4).
    const estrechoPreparcial = ctx => ctx.chart.width < 360;

    // Un valor de la etiqueta emergente con las cifras que hacen falta: los
    // conteos sin decimales («5», no «5.000»), las colas pequeñas con dos
    // cifras significativas («0.0017», no «0.002»; «0.0000096», no «0.000»)
    // y tres decimales entre 0.1 y 10, que son los que separan 1.019 de
    // 1.018 en las bandas (gráficos, ronda 5).
    function valorPreparcial(y) {
      if (Number.isInteger(y)) return String(y);
      const a = Math.abs(y);
      if (a >= 10) return y.toFixed(1);
      if (a >= 0.1) return y.toFixed(3);
      return String(+y.toPrecision(2));
    }

    // La leyenda y la etiqueta emergente, más compactas en el teléfono. En
    // un lienzo de 206 px la etiqueta emergente medía hasta 307 y se cortaba
    // sin dar el valor; ahora la letra, el relleno y la caja se encogen, y
    // cada conjunto puede traer un rótulo corto (`corto`) para el teléfono.
    // El rótulo de la etiqueta emergente prefiere `soloTooltip`, que nombra
    // los bordes de banda que la leyenda esconde o agrupa («Borde alto», y
    // no «Banda del modelo», como si la banda fuera un solo número). Leyenda
    // y etiqueta siguen el orden de los conjuntos, que es el del enunciado:
    // el `order` de Chart.js decide quién se pinta encima, no quién se lee
    // primero. `tituloRadio` pone el radio con su unidad; `titulo`, un
    // título propio a partir del punto.
    function pluginsPreparcial(filtro, opciones = {}) {
      const estrecho = estrechoPreparcial;
      const etiquetas = {
        font: ctx => ({ family: 'Montserrat', size: estrecho(ctx) ? 10 : 12 }),
        boxWidth: ctx => estrecho(ctx) ? 12 : 24,
        padding: ctx => estrecho(ctx) ? 6 : 10,
        sort: (a, b) => a.datasetIndex - b.datasetIndex
      };
      if (filtro) etiquetas.filter = filtro;
      const tooltip = {
        backgroundColor: '#012820',
        titleFont: ctx => ({ family: 'Montserrat', weight: 'bold', size: estrecho(ctx) ? 10 : 12 }),
        bodyFont: ctx => ({ family: 'Fira Code', size: estrecho(ctx) ? 10 : 12 }),
        padding: ctx => estrecho(ctx) ? 4 : 6,
        boxWidth: ctx => estrecho(ctx) ? 8 : 12,
        boxHeight: ctx => estrecho(ctx) ? 8 : 12,
        itemSort: (a, b) => a.datasetIndex - b.datasetIndex,
        callbacks: {
          label: it => {
            const largo = it.dataset.soloTooltip || it.dataset.label || '';
            const nombre = estrecho(it) && it.dataset.corto ? it.dataset.corto : largo;
            return (nombre ? nombre + ': ' : '') + valorPreparcial(it.parsed.y);
          }
        }
      };
      if (opciones.tituloRadio)
        tooltip.callbacks.title = its => its.length ? 'r = ' + milesPreparcial(its[0].parsed.x) + ' m' : '';
      else if (opciones.titulo)
        tooltip.callbacks.title = its => its.length ? opciones.titulo(its[0]) : '';
      return {
        legend: { display: !opciones.sinLeyenda, labels: etiquetas },
        tooltip: tooltip
      };
    }

    // Una marca vertical en un radio, dibujada encima de las curvas sin ser
    // un conjunto de datos. Como conjunto, sus dos puntos entraban en la
    // etiqueta emergente del modo 'index' («r = 3 638 m: 0.600» con el
    // ratón a 59 m) y dejaban un círculo suelto al pie de la marca, justo en
    // las distancias cortas que la pista manda mirar (gráficos, ronda 5). La
    // leyenda la nombra con un conjunto vacío del mismo trazo. Sin Chart.js
    // (la CDN caída) no se registra, y el resto del guion sigue en pie.
    if (typeof Chart !== 'undefined') Chart.register({
      id: 'marcaVertical',
      defaults: { x: null, color: '#475569', ancho: 1.5 },
      afterDatasetsDraw(chart, args, o) {
        if (o.x == null || !chart.scales.x) return;
        const a = chart.chartArea, px = chart.scales.x.getPixelForValue(o.x);
        if (!(px >= a.left && px <= a.right)) return;
        const ctx = chart.ctx;
        ctx.save();
        ctx.strokeStyle = o.color; ctx.lineWidth = o.ancho; ctx.setLineDash([2, 3]);
        ctx.beginPath(); ctx.moveTo(px, a.top); ctx.lineTo(px, a.bottom); ctx.stroke();
        ctx.restore();
      }
    });

    // Las referencias (la línea del 1, la del 5, los bordes de banda) en un
    // gris que pasa el 3:1 de contraste sobre blanco; el de la plantilla daba
    // 2.56:1, y son justo las líneas que nombran los enunciados.
    const GRIS_REFERENCIA = '#64748b';

    // Miles separados en los rótulos de los gráficos. En el texto la casa usa
    // el espacio fino, pero en el lienzo, con Montserrat a 11 px, mide 1.5 px
    // y detrás de un «1» no se ve: se leía «1320» y «1867» (gráficos, ronda
    // 5). Aquí va el espacio duro, que mide el doble.
    function milesPreparcial(v) {
      return Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    // Una serie como pares {x, y}, para los ejes lineales de r.
    function puntosXY(r, v) { return r.map((x, i) => ({ x: x, y: v[i] })); }

    // El eje de r en kilómetros, lineal y con una línea por kilómetro. Con
    // el eje de categorías las marcas caían en 59, 822, 1584… y ninguna en
    // 3 km, que es donde una pregunta pide leer.
    function ejeKmPreparcial(r) {
      return { type: 'linear', min: 0, max: Math.ceil(Math.max.apply(null, r) / 1000) * 1000,
               title: { display: true, text: 'r (km)', font: { family: 'Montserrat', size: 11 } },
               ticks: { stepSize: 1000, maxRotation: 0, callback: v => String(v / 1000),
                        font: { family: 'Montserrat', size: 11 } },
               grid: { display: true, color: 'rgba(148, 163, 184, 0.25)' } };
    }

""" + "".join(
    f"    AUTOEVALUACIONES['bloque-{clave}'] = [\n"
    + ",\n".join(js_pregunta(q) for q in preguntas)
    + "\n    ];\n\n"
    for clave, preguntas in PREGUNTAS.items()))

MODULOS = "".join(f(i + 1) for i, (f, _, _) in enumerate(CONSTRUCTORES))
MODULOS_NAV = [(t, d) for _, t, d in CONSTRUCTORES]
_mods = ",\n".join(f'        {{ id: {i + 1}, title: "{t}", duration: "{d}" }}'
                   for i, (t, d) in enumerate(MODULOS_NAV))
COURSE_DATA = f"""    const courseData = {{
      modules: [
{_mods}
      ]
    }};

    // El preparcial entero, tal como sale de precalculo/genera_preparcial2.R.
    // Cada cifra reutilizada trae de qué archivo y de qué ruta vino, que es lo
    // que permite a audita_preparcial2.py comprobar que el capítulo no se ha
    // movido debajo.
    const DATOS_PRE2 = {json.dumps(D, ensure_ascii=False)};
"""

VACIO_SIMULADORES = """    // Sin simuladores: este documento no enseña contenido nuevo. El registro se
    // deja vacío a propósito, para que cuenta_sitio.py no cuente los de
    // demostración de la plantilla como si fueran de este documento.

"""


def reemplaza_region(texto, abre, cierra, nuevo, que_, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes
    (de `ensambla_taller1.py`): sustituir de más se llevó 270 líneas del
    motor con el informe en verde, y de menos dejó vivos dos simuladores de
    demostración."""
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de «{que_}» aparece {texto.count(abre)} veces, no 1")
    i = texto.index(abre)
    j = texto.index(cierra, i) + len(cierra)
    n_lineas = texto[i:j].count("\n")
    if n_lineas > max_lineas:
        sys.exit(f"PARADO: la región de «{que_}» ocupa {n_lineas} líneas y el tope es {max_lineas}")
    if n_lineas < min_lineas:
        sys.exit(f"PARADO: la región de «{que_}» ocupa solo {n_lineas} líneas y el mínimo es {min_lineas}")
    print(f"  OK   {que_}  ({n_lineas} líneas sustituidas)")
    return texto[:i] + nuevo + texto[j:]


def sustituye(texto, ancla, nuevo, que_):
    veces = texto.count(ancla)
    if veces != 1:
        sys.exit(f"PARADO: el ancla de «{que_}» aparece {veces} veces, no 1.\n        {ancla[:90]!r}")
    print(f"  OK   {que_}")
    return texto.replace(ancla, nuevo, 1)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_preparcial2.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")
    demos = sorted(set(re.findall(r"[A-Z_]+\['(demo[^']*)'\]", doc))
                   | set(re.findall(r'data-[a-z-]+="(demo[^"]*)"', doc)))
    print(f"  componentes de demostración en la plantilla: {len(demos)} ({', '.join(demos)})\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Preparcial del Corte II — Estadística Espacial</title>", "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "PREPARCIAL DEL CORTE II •\n"
                    "              CAPÍTULOS 4 Y 5 • SIN NOTA • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Preparcial del Corte II •\n"
                    "          UnBosque 2026-II", "pie")
    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_PRE2", max_lineas=20)
    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los módulos del preparcial", max_lineas=600)
    doc = reemplaza_region(doc, "    MAPAS_ESTACIONALES['demo-mapa'] = function () {",
                           "\n    };\n", "", "el mapa estacional de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    GLOSARIOS['demo-notacion'] = {", "\n    };\n",
                           "", "el glosario de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    RUBRICAS['demo-rubrica'] = {", "\n    };\n",
                           "", "la rúbrica de demostración", max_lineas=40)
    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], "", "el mapa de demostración")
    doc = reemplaza_region(
        doc,
        "    // --- Deslizadores sobre un gráfico de línea ----------------------\n"
        "    SIMULADORES['demo-deslizadores'] = function (raiz) {",
        "    // ================================================================\n"
        "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        VACIO_SIMULADORES
        + "    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los simuladores de demostración", max_lineas=140, min_lineas=100)
    doc = reemplaza_region(doc, "    TABLAS_RANKING['demo'] = function () {", "\n    };\n",
                           "", "la tabla de ranking de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS, "las preguntas de los bloques", max_lineas=90)
    doc = reemplaza_region(doc, "    SIMULACROS['demo'] = {", "\n    };\n",
                           "", "el simulacro de demostración", max_lineas=40)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida: que el guion escriba no significa que escriba bien.
    marcado = "".join(re.findall(r'<template id="module-.*?</template>', doc, re.S))
    mods = doc.count('<template id="module-')
    declarados = len(MODULOS_NAV)
    try:
        donde = DESTINO.relative_to(RAIZ)
    except ValueError:
        donde = DESTINO
    n_preguntas = sum(len(v) for v in PREGUNTAS.values())
    por_tipo = {}
    for v in PREGUNTAS.values():
        for q in v:
            por_tipo[q["tipo"]] = por_tipo.get(q["tipo"], 0) + 1
    cubiertos = {f"{q['doc']}.m{q['modulo']}" for v in PREGUNTAS.values() for q in v}
    n_ej = marcado.count('class="ejercicio-guiado"')
    print(f"\n{donde}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos ({declarados} declarados) · {n_preguntas} preguntas · "
          f"{n_ej} ejercicios · {len(ERRORES)} errores · {marcado.count('<a href=')} enlaces")
    print("  tipos: " + " · ".join(f"{k} {v}" for k, v in sorted(por_tipo.items())))
    print(f"  módulos del alcance con pregunta propia: {len(cubiertos)} de {len(ALC.ALCANCE)}")

    problemas = []
    if mods != declarados:
        problemas.append(f"{mods} plantillas de módulo y {declarados} declaradas en la navegación")
    faltan_mod = [f"{f['doc']}.m{f['modulo']}" for f in ALC.ALCANCE
                  if f"{f['doc']}.m{f['modulo']}" not in cubiertos]
    if faltan_mod:
        problemas.append(f"módulos del alcance sin pregunta: {', '.join(faltan_mod)}")
    if n_ej != meta["n_ejercicios"]:
        problemas.append(f"el JSON trae {meta['n_ejercicios']} ejercicios y el documento pinta {n_ej}")
    # El nombre del catálogo, atado a su recuento (§12.7 del Corte I): «los
    # quince errores» se escribe con letra en tres sitios y no se actualiza solo.
    NOMBRE_RECUENTO = {15: "quince"}
    palabra = NOMBRE_RECUENTO.get(len(ERRORES))
    if palabra is None or marcado.count(f"{palabra} errores") < 2:
        problemas.append(f"el catálogo tiene {len(ERRORES)} errores y la prosa los llama "
                         f"«{palabra or '?'}»")
    sin_nombrar = [f"{f['doc']}.m{f['modulo']}" for f in ALC.ALCANCE if f["titulo"] not in marcado]
    if sin_nombrar:
        problemas.append(f"módulos del alcance sin nombrar: {', '.join(sin_nombrar)}")
    fuera_sin = [f"{f['doc']}.m{f['modulo']}" for f in ALC.FUERA_DE_ALCANCE if f["titulo"] not in marcado]
    if fuera_sin:
        problemas.append(f"módulos fuera del alcance sin nombrar: {', '.join(fuera_sin)}")
    restos = sorted(d for d in demos if f"'{d}'" in doc or f'"{d}"' in doc)
    if restos:
        problemas.append(f"quedan componentes de demostración: {', '.join(restos)}")
    if "<U+" in doc:
        problemas.append("el documento lleva codificación rota (<U+…>)")
    problemas.extend(revisa_preguntas())
    registradas = len(re.findall(r"\n    AUTOEVALUACIONES\['", doc))
    contenedores = len(re.findall(r'data-quiz="', marcado))
    if registradas != contenedores:
        problemas.append(f"{registradas} cuestionarios registrados y {contenedores} contenedores")
    huerfanas = sorted(set(PRESENTA) - USADAS)
    if huerfanas:
        problemas.append(f"PRESENTA declara cifras que no se citan: {', '.join(huerfanas)}")
    # Ninguna cifra reutilizada sin leer: un campo que ninguna página lee suele
    # ser una advertencia que nunca llegó a escribirse. Las series de gráfico
    # cuentan como leídas si algún gráfico las declara en su `desde`.
    # `desde` llega como objeto con nombre —serie: {origen, ruta}—, no como lista.
    rutas_graf = {d["ruta"] for g in GR.values() for d in (g.get("desde") or {}).values()}
    muertas = sorted(k for k, v in REU.items()
                     if k not in USADAS and not (isinstance(v["valor"], list) and v["ruta"] in rutas_graf))
    if muertas:
        problemas.append(f"cifras reutilizadas que nadie cita: {', '.join(muertas)}")

    if problemas:
        print()
        for p in problemas:
            print(f"  MAL  {p}")
        print()
        return 1
    print("  todas las guardas de salida en verde\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
