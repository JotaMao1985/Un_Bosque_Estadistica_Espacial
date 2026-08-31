#!/usr/bin/env python3
"""
ensambla_preparcial1.py — construye el preparcial del Corte I · P2.1

Material de Estadística Espacial 2026-II (20929).
Ver PLAN_Preparcial_Corte_1.md.

El documento tiene hoy siete módulos: el que dice qué entra en el parcial,
los cuatro bloques de preguntas —A y B en P2.2, C y D en P2.3—, las seis
rutinas con salida ejecutada, y el catálogo de errores. Los seis ejercicios
guiados son P2.4 y entran entre el bloque D y el catálogo.

LOS MÓDULOS SE NUMERAN SOLOS, Y ES LA DECISIÓN QUE SOSTIENE LAS TAREAS QUE
FALTAN. El motor exige que la navegación declare exactamente los módulos que
existen y que vayan del 1 al N sin huecos: un botón que abre un `template`
inexistente deja el panel en blanco **sin un solo error en consola**, que es
el modo de fallo más caro de esta plantilla. Por eso aquí no hay números de
módulo escritos: hay una lista ordenada de constructores, y el número, la
cabecera y la entrada de navegación salen de la posición. Insertar los cuatro
bloques entre el primero y el último renumera todo sin tocar una línea.

Consecuencia práctica: el módulo de cierre era el **2** cuando solo estaban
los dos que enmarcan, es el **7** ahora y será el **8** cuando entren los
ejercicios guiados. No hay que acordarse de nada ni renumerar nada.

LOS SEIS PROCEDIMIENTOS SE EJECUTARON PARA ESCRIBIR SUS `#>`, y no se pueden
tocar de memoria: `verifica_bloques.py` los vuelve a ejecutar encadenados y
contrasta cada cifra anunciada contra la salida real. Dos avisos que costaron
encontrarlos: el estado de `sf_use_s2()` es **global**, así que el bloque que
mide distancias lo fija y lo restaura —si no, su resultado depende de qué
capítulo se ejecutó antes en la misma sesión—; y un bloque de código con una
barra invertida no puede ir interpolado en una f-string, porque el intérprete
del proyecto es 3.10. Por eso los seis van CONCATENADOS —cerrar la cadena,
sumar `tabs(...)`, abrir otra— y no interpolados, igual que en
`ensambla_cap1.py`.

NINGUNA CIFRA A MANO (D10), y aquí con un agravante: este documento cita
cifras que calcularon los capítulos 1, 2 y 3. Todas entran por `val()`, que
las saca de `preparcial1_datos.json`, y el JSON guarda de qué archivo y de
qué ruta vino cada una para que `audita_preparcial1.py` pueda volver a
resolverlas contra el capítulo. Lo único que este archivo decide sobre una
cifra es **cuántos decimales y qué unidad** se le ponen al mostrarla, que es
presentación y no cálculo.

EL ENLACE AL MÓDULO EXACTO NO EXISTE TODAVÍA. La plantilla no tiene enlaces
profundos —`loadModule()` no mira el hash— y construirlos es P0.2, aplazada
por la fecha. Mientras tanto, todo enlace a un módulo de un capítulo pasa por
`enlace_modulo()`, que hoy lleva a la portada del capítulo y nombra el módulo
en el texto. Cuando P0.2 exista, se añade el `#m{n}` en esa única función.

Uso:  python3 precalculo/ensambla_preparcial1.py
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
import alcance_preparcial1 as ALC  # noqa: E402


def _ruta(var: str, defecto: pathlib.Path) -> pathlib.Path:
    """La ruta publicada, o la copia que apunte la variable de entorno.

    Mismo convenio que los ensambladores de capítulo y el del taller: es lo
    que permite que un arnés de inyección construya desde JSON envenenados
    sin escribir jamás sobre lo publicado.
    """
    p = pathlib.Path(os.environ.get(var) or defecto)
    if var.endswith("DESTINO"):
        return p
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return p


PLANTILLA = _ruta("PREPARCIAL1_PLANTILLA", RAIZ / "plantilla" / "plantilla-capitulo.html")
DESTINO = _ruta("PREPARCIAL1_DESTINO", RAIZ / "Htmls_Espacial" / "preparcial-corte-1.html")
D = json.loads(_ruta("PREPARCIAL1_DATOS", SALIDAS / "preparcial1_datos.json")
               .read_text(encoding="utf-8"))

meta, REU, ERRORES = D["meta"], D["reutilizado"], D["errores"]


# ---------------------------------------------------------------------
# Formateadores. Los cuatro nombres que `sin_aritmetica.py` vigila: si
# dentro de uno de ellos aparece una operación aritmética fuera de un
# bloque de código, esa cifra se está calculando aquí en vez de en R.
# ---------------------------------------------------------------------
def n(x, d=5):
    """Punto decimal y cinco cifras, la regla del material desde el 2026-08-03."""
    return f"{float(x):.{d}f}"


def n5(x):
    return n(x, 5)


def ent(x):
    """Entero con separador de millar fino (U+202F), fuera de fórmulas."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_mate(x):
    return f"{int(round(float(x))):,}".replace(",", r"\,")


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(iso):
    """«2026-09-01» leído como lo lee una persona.

    Es presentación, no cálculo: la fecha viene del JSON y aquí solo se
    escribe en castellano. Una fecha ISO en mitad de una frase se lee como
    un identificador y no como un día, y este documento existe para que
    alguien sepa cuánto le queda.
    """
    d = datetime.date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def val(clave):
    if clave not in REU:
        sys.exit(f"PARADO: la cifra «{clave}» no está en preparcial1_datos.json")
    return REU[clave]["valor"]


def que(clave):
    return REU[clave]["que"]


def val_nuevo(ruta):
    """El valor de un cálculo nuevo, por su ruta dentro de `nuevo`."""
    cur = D["nuevo"]
    for parte in ruta.split("."):
        if not isinstance(cur, dict) or parte not in cur:
            sys.exit(f"PARADO: la ruta «{ruta}» no existe en nuevo")
        cur = cur[parte]
    return cur


# ---------------------------------------------------------------------
# Cómo se muestra cada cifra citada. Decimales y unidad son PRESENTACIÓN:
# el valor sale del JSON y esto solo decide cómo se lee. Se escribe una a
# una y no por regla automática porque «0.00000 km²» y «4890691.57534 m»
# son las dos formas de publicar una cifra correcta e ilegible.
# ---------------------------------------------------------------------
# Unidades que se escriben pegadas al número.
PEGADAS = {"°"}

PRESENTA = {
    # Las de magnitud grande van sin decimales a propósito: «4 890 691.58 m»
    # publica dos centímetros de precisión sobre una cifra cuyo argumento es
    # que son millones de metros, y de paso obliga a mezclar el separador de
    # millar con la coma decimal, que en los capítulos no aparece nunca.
    "etiq_set_crs":         (0, "m"),
    "etiq_transform":       (0, "m"),
    "etiq_lon_absurda":     (0, "°"),
    "csv_desplaz_med":      (0, "km"),
    "csv_en_colombia":      (0, ""),
    "csv_hubo_aviso":       (0, ""),
    "c3m2_r":               (5, ""),
    "c3m2_solape":          (0, ""),
    "c3m2_pct_est":         (5, "%"),
    "inf_cobertura_phi4":   (5, ""),
    "inf_factor_phi4":      (5, "veces"),
    "inf_inflacion":        (5, "%"),
    "cv_rmse_alea":         (5, "°C"),
    "cv_rmse_bloques":      (5, "°C"),
    "cv_inflacion":         (5, "%"),
    "c3m8_r_ind":           (5, ""),
    "c3m8_r_dep":           (5, ""),
    "c3m8_subida":          (5, "%"),
    "c3m5_dE_normal":       (5, ""),
    "c3m5_dE_deuter":       (5, ""),
    "c3m5_caida":           (5, "%"),
    "c3m3_empatados":       (0, ""),
    "c3m3_convenio_r":      (0, ""),
    "c3m3_convenio_py":     (0, ""),
    # Ocho diezmilmillonésimas de kilómetro cuadrado. Con cinco decimales se
    # publicaría «0.00000», que es exactamente lo que la cifra quiere
    # desmentir: el área no es pequeña, es que no es un área.
    "topo_buffer_grados":   (10, "km²"),
    "topo_buffer_3857":     (5, "km²"),
    # --- las que citan las preguntas de los bloques A y B ---
    "snow_pct_broad":       (5, "%"),
    "snow_razon_uniforme":  (5, "veces"),
    "ce_redwood":           (5, ""),
    "ce_pinos":             (5, ""),
    "ce_celulas":           (5, ""),
    "tobler_ideam_b1":      (5, ""),
    "tobler_perm_b1":       (5, ""),
    "tobler_esperado":      (5, ""),
    "tobler_caida_alt":     (5, "%"),
    "inf_cobertura_ind":    (5, ""),
    "inf_cobertura_phi16":  (5, ""),
    "neff_desercion":       (2, ""),
    "neff_desercion_n":     (0, ""),
    "neff_rho_implicito":   (5, ""),
    "neff_pct":             (5, "%"),
    "neff_I_primera_banda": (5, ""),
    "realiz_n":             (0, ""),
    "realiz_rechaza":       (0, "%"),
    "realiz_esperado":      (0, "%"),
    "realiz_sd_medias":     (5, ""),
    "realiz_emc":           (5, "puntos"),
    "escala_moran_mun":     (5, ""),
    "escala_moran_dep":     (5, ""),
    "escala_caida":         (5, "%"),
    "escala_n_dep":         (0, ""),
    "anat_filas":           (0, ""),
    "anat_pct_geom":        (5, "%"),
    "anat_vertices":        (0, ""),
    "anat_multiples":       (0, ""),
    "cv_r2_bloques":        (5, ""),
    "elip_a_menos_b":       (2, "m"),
    "elip_datum_desp":      (2, "m"),
    "epsg_3116_max":        (5, "%"),
    "epsg_9377_max":        (5, "%"),
    "epsg_3116_med":        (5, "%"),
    "epsg_9377_med":        (5, "%"),
    "etiq_silencioso":      (0, "m"),
    "etiq_n_localidades":   (0, ""),
    "form_campos_largos":   (0, ""),
    "form_n_rasgos":        (0, ""),
    "form_n_campos":        (0, ""),
    "form_logico":          (0, ""),
    "form_gpkg_razon":      (5, ""),
    "form_geojson_razon":   (5, ""),
    "pos_tasa_global":      (5, "%"),
    "pos_razon_max_min":    (5, ""),
    "pos_corr":             (5, ""),
    "topo_area_antes":      (0, ""),
    "topo_area_despues":    (0, ""),
    "ing_pares_bruta":      (0, ""),
    "ing_pares_cajas":      (0, ""),
    "ing_reduccion":        (5, "veces"),
    # --- las que citan las preguntas del bloque C, capítulo 3 ---
    "c3m1_config":          (0, ""),
    "c3m1_distintos":       (0, ""),
    "c3m1_pct":             (5, "%"),
    "c3m1_vacias":          (0, ""),
    "c3m2_rho":             (5, ""),
    "c3m2_pct_mun":         (5, "%"),
    "c3m4_discordante":     (5, "%"),
    "c3m4_concordante":     (5, "%"),
    "c3m4_estables":        (5, "%"),
    "c3m4_rango_max":       (0, ""),
    "c3m5_comparaciones":   (0, ""),
    "c3m6_verbos":          (0, ""),
    "c3m6_version":         (0, ""),
    "c3m7_por_punto":       (0, ""),
    "c3m7_n_puntos":        (0, ""),
    "c3m7_hexagonos":       (0, ""),
    "c3m7_razon_simbolos":  (5, "veces"),
    "c3m8_r_mun":           (5, ""),
    "c3m8_pct_var":         (5, "%"),
    # --- las que citan las preguntas del bloque D, que cruzan capítulos ---
    "pos_sedes_por_pos":    (5, ""),
    "ing_vecino_mediana":   (2, "m"),
    "medir_dist_max":       (2, "m"),
    "grad_bogota_oslo":     (5, "veces"),
    # Los cálculos nuevos que cita el catálogo, por su ruta dentro de `nuevo`.
    "euclidea_grados.n_estaciones":    (0, ""),
    "euclidea_grados.error_med_pct":   (5, "%"),
    "euclidea_grados.error_max_pct":   (5, "%"),
    "euclidea_grados.pct_sobreestima": (0, "%"),
    "convenio_intervalo.primera_clase_r":      (0, ""),
    "convenio_intervalo.primera_clase_python": (0, ""),
    "convenio_intervalo.movidos_primera":      (0, ""),
}



# Qué cifras se han citado de verdad. Lo llena `cifra()` al ejecutarse, no
# quien la llama: la primera versión lo apuntaba en el envoltorio que usan las
# preguntas, y las del catálogo de errores —que llaman a `cifra()` directa—
# quedaban sin registrar. La guarda de huérfanas denunciaba entonces catorce
# cifras que sí se usan.
USADAS = set()


def cifra(clave, v=None):
    """El valor de una cifra citada, ya vestido para leerse.

    El espacio entre el número y su unidad es `&nbsp;` y no un espacio
    normal: es la convención de los capítulos y evita que «4 890 691 m» se
    parta al final de una línea. La primera versión lo pegaba —«0m»,
    «10293.14km»— porque la unidad iba dentro de la misma cadena.
    """
    if clave not in PRESENTA:
        sys.exit(f"PARADO: «{clave}» se cita sin decir con cuántos decimales "
                 f"ni en qué unidad se muestra (añádela a PRESENTA)")
    USADAS.add(clave)
    decimales, unidad = PRESENTA[clave]
    if v is None:
        v = val(clave)
    if isinstance(v, bool):
        return "<strong>no</strong>" if not v else "<strong>sí</strong>"
    if isinstance(v, str):
        return f"<code>{v}</code>"
    texto = ent(v) if decimales == 0 else n(v, decimales)
    if not unidad:
        return texto
    # El grado se pega al número —«7.0760°», como lo escribe el capítulo 2— y
    # el resto de unidades van separadas. Sin esto salía «4 890 618 °».
    return f"{texto}{unidad}" if unidad in PEGADAS else f"{texto}&nbsp;{unidad}"


def enlace_modulo(doc, modulo, texto):
    """El enlace a un módulo de un capítulo — el único sitio donde se arma.

    Hoy lleva a la portada del capítulo, porque el enlace profundo es P0.2 y
    está aplazado. El número del módulo va en el texto, así que el enlace
    sigue diciendo adónde ir aunque no lleve solo. Cuando P0.2 exista, se
    añade `#m{modulo}` aquí y los 40 y pico enlaces del documento lo heredan.
    """
    return f'<a href="{ALC.DOCS[doc]}">{texto}</a>'


NOMBRE_CAP = {
    "cap1": "Capítulo 1 · Datos espaciales y la primera ley de la geografía",
    "cap2": "Capítulo 2 · SIG, sistemas de referencia y georreferenciación con sf",
    "cap3": "Capítulo 3 · Cartografía estadística y el MAUP",
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
# Cada una declara el módulo del CAPÍTULO que evalúa, no el bloque del
# preparcial en el que vive: de ahí sale el `repaso` que el resumen del
# cuestionario usa para mandar al sitio exacto. Un guion que declarase el
# módulo propio mandaría a repasar el bloque que acaba de hacerse.
#
# Toda opción lleva su `retro`, también las correctas, y las incorrectas
# explican a qué error llevan. Es la regla del motor y aquí se comprueba:
# una opción sin retroalimentación, con retroalimentación vacía o con la
# misma que una hermana para el ensamblado.
# =====================================================================
def op(texto, correcta, retro):
    return {"texto": texto, "correcta": correcta, "retro": retro}


def preg(tipo, doc, modulo, pregunta, pista, **kw):
    if not ALC.en_alcance(doc, modulo):
        sys.exit(f"PARADO: una pregunta apunta a {doc}.m{modulo}, fuera del alcance")
    q = {"tipo": tipo, "doc": doc, "modulo": modulo,
         "pregunta": pregunta, "pista": pista}
    q.update(kw)
    return q


def cn(ruta):
    """Una cifra de los cálculos nuevos, por su ruta dentro de `nuevo`."""
    return cifra(ruta, val_nuevo(ruta))


c = cifra
N1 = D["nuevo"]["n_efectivo"]
N2 = D["nuevo"]["grado_longitud"]
# Las cinco que ganaron distractores para poder viajar a un banco del LMS,
# donde una pregunta de respuesta abierta no entra. Nombrar aquí la cifra de
# cada error concreto es además mejor retroalimentación que «un porcentaje
# bastante menor»: quien se equivocó se reconoce en el número.
N3 = D["nuevo"]["convenio_intervalo"]
N5 = D["nuevo"]["cv_inflacion"]
N6 = D["nuevo"]["indice_espacial"]
N8 = D["nuevo"]["caida_color"]
N9 = D["nuevo"]["efecto_escala"]


def dist(item, id_):
    """El valor de un distractor calculado, por su identificador."""
    for d in item["distractores"]:
        if d["id"] == id_:
            return n(d["valor"], item["decimales"])
    sys.exit(f"PARADO: no hay distractor «{id_}»")


# ---------------------------------------------------------------------
# BLOQUE A · capítulo 1
# ---------------------------------------------------------------------
BLOQUE_A = [
    preg("opcion", "cap1", 1,
         f"En el brote de Broad Street, el {c('snow_pct_broad')} de las muertes tiene "
         f"esa bomba como la más cercana, {c('snow_razon_uniforme')} por encima de lo "
         f"que cabría esperar si las trece bombas fueran intercambiables. "
         f"<strong>Por sí solo</strong>, ¿qué permite concluir ese patrón?",
         "Distingue entre lo que el patrón descarta y lo que el patrón explica.",
         opciones=[
             op("Que la distribución de las muertes no es compatible con trece bombas intercambiables.",
                True,
                "Eso y no más. El patrón <em>descarta</em> una hipótesis —que la bomba usada da igual— "
                "y ese descarte es el argumento de Snow. Lo demás vino de la investigación de campo."),
             op("Que el agua de esa bomba causó los casos.", False,
                "La proximidad no es exposición. Que la bomba más cercana sea esa no dice que la "
                "víctima bebiera de ella, y el paso de patrón a causa lo dio Snow con trabajo de "
                "campo —los casos lejanos que sí iban a Broad Street—, no con el mapa."),
             op("Que esa misma proporción de enfermos bebió de esa bomba.", False,
                "Confunde «bomba más cercana» con «bomba usada». El mapa mide distancias, no "
                "conductas: es la primera traducción que hay que negarse a hacer."),
             op("Que la bomba está en el centro del barrio más poblado.", False,
                "Es una explicación rival legítima, y por eso mismo no es una conclusión: es lo que "
                "el argumento tiene que descartar aparte. Un patrón de puntos sin denominador no "
                "distingue «más casos» de «más gente».")]),

    preg("multiple", "cap1", 2,
         f"El índice de Clark-Evans da {c('ce_redwood')} en las plántulas de secuoya, "
         f"{c('ce_pinos')} en los pinos japoneses y {c('ce_celulas')} en las células. "
         f"Marca <strong>todo</strong> lo que se puede afirmar.",
         "R compara la distancia media al vecino más cercano con la esperada bajo CSR. "
         "Son dos.",
         opciones=[
             op("Un valor por debajo de 1 indica agregación.", True,
                "Los vecinos están más cerca de lo que la aleatoriedad predice: los puntos se apiñan."),
             op("Las células están dispuestas más regularmente que un proceso aleatorio.", True,
                "Por encima de 1 los vecinos están más lejos de lo esperado, que es lo que produce "
                "una inhibición: cada célula ocupa un espacio que las demás no pueden ocupar."),
             op("Un valor por encima de 1 indica que hay más puntos de los esperados.", False,
                "Confunde intensidad con disposición. R no mide cuántos puntos hay —eso es λ—, "
                "mide cómo están repartidos. Un patrón regular y uno agregado pueden tener la misma λ."),
             op("El índice mide la misma propiedad que el Moran I.", False,
                "No: Clark-Evans describe un <strong>patrón puntual</strong>, donde lo aleatorio es "
                "la posición; el Moran I describe un <strong>dato de área</strong>, donde las "
                "posiciones están fijas y lo aleatorio es el valor. Es la distinción del módulo 2 y "
                "la que decide qué método aplica.")],
         retroAcierto="Las dos que se sostienen dicen lo mismo por los dos lados: por debajo "
                      "de 1 los vecinos están más cerca de lo que la aleatoriedad predice, y por "
                      "encima más lejos. R mide disposición, no cantidad.",
         retroFallo="Se sostienen la lectura del valor por debajo de 1 y la de las células. Las "
                    "otras dos confunden disposición con intensidad, y patrón puntual con dato "
                    "de área."),

    preg("opcion", "cap1", 3,
         f"Sobre las estaciones del IDEAM, el Moran I de la primera banda de distancia vale "
         f"{c('tobler_ideam_b1')}. Permutando las temperaturas al azar entre las mismas "
         f"estaciones baja a {c('tobler_perm_b1')}, y el valor esperado bajo independencia "
         f"es {c('tobler_esperado')}. ¿Qué papel juega la permutación?",
         "¿Qué cambia al permutar y qué se queda igual?",
         opciones=[
             op("Da la referencia empírica de «sin ley»: lo que sale cuando la posición ya no "
                "lleva información.", True,
                "Las estaciones siguen donde estaban y las distancias son las mismas; lo único que "
                "se rompe es el vínculo entre lugar y valor. Por eso el valor permutado es con lo "
                "que hay que comparar, y no con cero."),
             op("Corrige el sesgo del estimador del Moran I.", False,
                "No corrige nada: es una referencia, no un ajuste. El sesgo del estimador es otra "
                "cosa y se ve en que el valor esperado bajo independencia no es cero, sino "
                f"{c('tobler_esperado')}."),
             op("Demuestra que la temperatura depende de la altitud.", False,
                "Eso lo mide otra comparación —descontar la altitud baja la autocorrelación un "
                f"{c('tobler_caida_alt')}—, no la permutación, que no sabe nada de altitud."),
             op("Aumenta el tamaño de muestra disponible.", False,
                "El número de estaciones no cambia. Lo que se genera son escenarios del mismo "
                "tamaño bajo una hipótesis nula, que es justo lo contrario de tener más datos.")]),

    preg("grafico", "cap1", 4,
         "El gráfico traza la cobertura real de un intervalo de confianza construido al "
         "95 % con la fórmula clásica, según cuánta dependencia espacial hay en los datos "
         "(φ crece hacia la derecha). ¿Qué se lee?",
         "Mira dónde empieza la curva y adónde llega, y compárala con la línea del 95 %.",
         alto=230,
         descripcionGrafico="Curva descendente de la cobertura real de un IC nominal al 95 % "
                            "conforme aumenta la dependencia espacial, con la línea del 95 % de referencia",
         dibujar="""canvas => {
            const g = DATOS_PRE1.graficos.g_cobertura;
            return crearGraficoLinea(canvas, g.phi.map(x => String(x)), [
              { label: 'Cobertura real', data: g.cobertura,
                borderColor: COLORES_GRAFICO.primario, backgroundColor: 'transparent',
                tension: 0.25, pointRadius: 3, borderWidth: 2 },
              { label: 'Nominal 95 %', data: g.phi.map(() => 0.95),
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent',
                borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5 }
            ]);
          }""",
         opciones=[
             op("Que el intervalo nominal al 95 % cubre cada vez menos a medida que crece la "
                "dependencia.", True,
                f"Con datos independientes la cobertura es {c('inf_cobertura_ind')}, lo prometido. "
                f"Con dependencia fuerte cae a {c('inf_cobertura_phi4')}, y en el extremo derecho "
                f"de la curva a {c('inf_cobertura_phi16')}: el intervalo sigue diciendo 95 y cada "
                "vez cumple menos."),
             op("Que el intervalo se vuelve más ancho al aumentar la dependencia.", False,
                "Es al revés, y ahí está la trampa: la fórmula clásica no sabe que hay dependencia, "
                "así que <em>no</em> ensancha nada. El intervalo se queda igual de estrecho mientras "
                "la variabilidad real crece por debajo."),
             op("Que el estimador de la media se vuelve sesgado.", False,
                "La media sigue siendo insesgada. Lo que se rompe es su <strong>error estándar</strong>, "
                f"subestimado {c('inf_factor_phi4')}, y con él todo lo que se construya encima."),
             op("Que la cobertura baja porque hay menos observaciones.", False,
                "El número de observaciones es el mismo en toda la curva. Lo que baja es cuánta "
                "información aporta cada una, y eso es el tamaño efectivo del módulo 5.")]),

    preg("numerica", "cap1", 5,
         f"Los {c('neff_desercion_n')} municipios con dato de deserción tienen una "
         f"correlación media de {c('neff_rho_implicito')}. ¿Cuál es el tamaño efectivo de "
         f"muestra? Da dos decimales.",
         "n<sub>eff</sub> = n / (1 + (n−1)ρ).",
         respuesta=float(val("neff_desercion")), tolerancia=0.5,
         retroAcierto=f"{c('neff_desercion')}: los {c('neff_desercion_n')} municipios "
                      f"aportan solo el {c('neff_pct')} de la información que tendrían "
                      f"si fueran independientes.",
         retroFallo=f"Son {c('neff_desercion')}. Si te salió {dist(N1, 'resta_lineal')}, "
                    f"descontaste la correlación linealmente en vez de dividir por el efecto "
                    f"de diseño. Si te salió {dist(N1, 'rho_primera_banda')}, usaste el Moran "
                    f"de la primera banda ({c('neff_I_primera_banda')}) como si fuera el ρ "
                    f"medio: la correlación de los vecinos inmediatos no es la correlación "
                    f"media. Y si te salió {dist(N1, 'multiplica')}, multiplicaste por el "
                    f"efecto de diseño en vez de dividir."),

    preg("opcion", "cap1", 6,
         f"Simulando {c('realiz_n')} realizaciones del mismo proceso espacial, la prueba "
         f"clásica rechaza la hipótesis nula el {c('realiz_rechaza')} de las veces cuando "
         f"debería rechazarla el {c('realiz_esperado')}, y la media de cada realización varía "
         f"con una desviación de {c('realiz_sd_medias')}. ¿Qué problema ilustra?",
         f"En la realidad no hay {c('realiz_n')} realizaciones: hay una.",
         opciones=[
             op("Que con una sola realización no se puede separar lo que dice el proceso de lo "
                "que dice esa realización concreta.", True,
                f"Es el problema fundamental del capítulo 1. Las {c('realiz_n')} realizaciones "
                "existen en la simulación para <em>medir</em> esa variabilidad; en un mapa "
                "real solo se ve una, y no viene marcada como típica o atípica."),
             op("Que el estimador de la media está sesgado.", False,
                "No lo está: la media de las medias cae sobre la media del proceso. Lo que es "
                "grande es su dispersión, y eso es varianza, no sesgo."),
             op(f"Que {c('realiz_n')} realizaciones son pocas para estabilizar el resultado.",
                False,
                f"El error de Monte Carlo del porcentaje de rechazo es de {c('realiz_emc')}: "
                f"{c('realiz_n')} bastan de sobra. El problema no es cuántas se simulan, es "
                "cuántas se observan."),
             op("Que la semilla elegida produce un caso extremo.", False,
                f"El resultado es el agregado de {c('realiz_n')} semillas distintas. Culpar a "
                "la semilla es justamente el razonamiento que el experimento desmonta.")]),

    preg("opcion", "cap1", 7,
         f"La deserción escolar tiene un Moran I de {c('escala_moran_mun')} a nivel "
         f"municipal y de {c('escala_moran_dep')} agregada a departamento: una caída del "
         f"{c('escala_caida')}. ¿Qué lo explica mejor?",
         "¿Qué le pasa a la variabilidad de corto alcance cuando se promedia dentro de una unidad grande?",
         opciones=[
             op("Que al agregar, la variación de corto alcance se promedia dentro de cada "
                "departamento y queda menos estructura entre departamentos.", True,
                "La agregación se come justo la escala en la que vivía la dependencia. Es el efecto "
                "escala del MAUP, y por eso el capítulo 3 lo retoma con datos individuales."),
             op("Que los departamentos son en el fondo menos dependientes entre sí que los "
                "municipios.", False,
                "«Los departamentos» no son otro fenómeno: son los mismos datos sumados. Atribuir la "
                "caída a una propiedad del nivel superior es tratar como hallazgo lo que es "
                "consecuencia de la agregación."),
             op("Que el Moran I no se puede comparar entre niveles de agregación.", False,
                "Es cierto que no es la misma cantidad —cambian las unidades, los vecinos y n— y "
                "conviene decirlo. Pero eso explica por qué la comparación es delicada, no por qué "
                "la caída va en esta dirección y no en la contraria."),
             op(f"Que con {c('escala_n_dep')} unidades el test pierde potencia.", False,
                "Confunde magnitud con significación. La potencia afecta al valor p, no al valor del "
                "índice: aquí lo que cae es el índice mismo.")]),

    preg("opcion", "cap1", 8,
         "Tienes las coordenadas de los árboles de una parcela y quieres saber si están más "
         "agrupados de lo que cabría esperar por azar. ¿Qué paquete de R hace ese trabajo?",
         "Pregúntate primero qué es aleatorio en tu dato: ¿la posición, o el valor en una posición fija?",
         opciones=[
             op("<code>spatstat</code>, porque el dato es un patrón puntual.", True,
                "Lo aleatorio son las posiciones, así que el objeto es un <code>ppp</code> con su "
                "ventana, y ahí viven la función K, la G y las pruebas de CSR."),
             op("<code>spdep</code>, porque va a hacer falta una matriz de pesos.", False,
                "<code>spdep</code> es para datos de <strong>área</strong>: unidades fijas con un "
                "valor cada una. Convertir los árboles en conteos por celda para poder usarlo es una "
                "decisión de modelado que cambia la pregunta, no un detalle técnico."),
             op("<code>gstat</code>, porque hay que estimar un variograma.", False,
                "<code>gstat</code> es para datos <strong>geoestadísticos</strong>: una variable "
                "continua medida en unos puntos, donde lo aleatorio es el valor y no la posición. "
                "Aquí no hay ninguna variable medida: hay presencias."),
             op("<code>sf</code>, porque es el que maneja la geometría.", False,
                "<code>sf</code> guarda y opera la geometría, y hace falta antes que nada, pero no "
                "responde preguntas de patrón: no tiene función K ni pruebas de aleatoriedad.")]),

    preg("opcion", "cap1", 9,
         f"En los {c('anat_filas')} condados de <code>nc</code>, la geometría ocupa el "
         f"{c('anat_pct_geom')} de los bytes del objeto, con {c('anat_vertices')} vértices "
         f"y {c('anat_multiples')} condados formados por más de una parte. ¿Qué implica "
         f"para el trabajo con el archivo?",
         "¿Dónde está el peso, en las columnas o en la geometría?",
         opciones=[
             op("Que quitar columnas de atributos apenas aligera: lo que pesa es la geometría, y lo "
                "que la aligera es simplificarla.", True,
                "La mayor parte de los bytes son coordenadas. Es la razón de que este material "
                "presupueste la geometría aparte y la simplifique con tolerancia medida."),
             op("Que conviene guardar en shapefile, que es más compacto.", False,
                f"Compacto lo es —el GeoPackage pesa {c('form_gpkg_razon')}&nbsp;veces el "
                "shapefile—, pero eso no cambia dónde está el peso: la geometría es la misma "
                "en los dos, y "
                "quien la guarda cambia de envase, no de tamaño. Y el shapefile trae de propina el "
                "truncado de nombres de campo y la pérdida del tipo lógico del módulo 7 del "
                "capítulo 2."),
             op("Que los condados con varias partes son un defecto de la fuente que hay que "
                "corregir.", False,
                "Son islas y enclaves reales. Un <code>MULTIPOLYGON</code> con varias partes es "
                "geometría legítima, y «arreglarlo» quedándose con la parte mayor borra territorio."),
             op("Que el objeto es demasiado grande para trabajar en memoria.", False,
                "El objeto entra de sobra en memoria. La cifra no habla de un límite, habla de "
                "una proporción: dice en qué "
                "vale la pena intervenir si algún día el tamaño importa.")]),

    preg("numerica", "cap1", 10,
         f"Un modelo de temperatura sobre las estaciones del IDEAM da un RMSE de "
         f"{c('cv_rmse_alea')} con validación cruzada aleatoria y de {c('cv_rmse_bloques')} "
         f"con validación cruzada por bloques espaciales. ¿En qué porcentaje es el error por "
         f"bloques mayor que el que anuncia la validación aleatoria? Da dos decimales.",
         "La base es el error que anuncia la CV aleatoria: ¿cuánto hay que subirlo, en tanto por "
         "ciento de sí mismo, para llegar al de bloques?",
         respuesta=float(val("cv_inflacion")), tolerancia=1.0,
         retroAcierto=f"Un {c('cv_inflacion')}. Con la CV aleatoria el vecino de cada punto suele "
                      f"caer en el pliegue de entrenamiento, así que el modelo se evalúa sobre "
                      f"puntos que ya conoce por interpolación.",
         retroFallo=f"Es un {c('cv_inflacion')}. Si te salió {dist(N5, 'base_bloques')}, "
                    f"tomaste como base el error por bloques en vez del de la CV aleatoria: lo que "
                    f"se infla es el optimista, así que el denominador es él. Si te salió "
                    f"{dist(N5, 'razon')}, diste la razón entre los dos errores y no el "
                    f"incremento: ese 100 % de partida ya está en el modelo. Y si te salió "
                    f"{dist(N5, 'cuadraticos')}, comparaste los errores cuadráticos en vez de sus "
                    f"raíces, que es hablar de MSE donde la pregunta dice RMSE. Y hay una cifra que "
                    f"lo dice todavía más claro: el "
                    f"R² por bloques es {c('cv_r2_bloques')} —negativo—, es decir, peor que "
                    f"predecir siempre la media. El mismo modelo que parecía explicar buena parte "
                    f"de la varianza no explica nada en cuanto se le pide extrapolar a una zona "
                    f"que no vio."),

    preg("opcion", "cap1", 11,
         "En la notación del curso, ¿qué distingue a <em>Z</em>(<em>s</em>) de "
         "<em>z</em>(<em>s</em>)?",
         "Una de las dos es lo que se observa; la otra, lo que se querría conocer.",
         opciones=[
             op("<em>Z</em>(<em>s</em>) es el proceso aleatorio y <em>z</em>(<em>s</em>) la "
                "realización observada.", True,
                "Mayúscula para la variable aleatoria, minúscula para el valor que se midió. La "
                "distinción es la que da sentido al problema de la única realización: se infiere "
                "sobre <em>Z</em> teniendo una sola <em>z</em>."),
             op("<em>Z</em>(<em>s</em>) es el valor medido y <em>z</em>(<em>s</em>) su versión "
                "estandarizada.", False,
                "Es el convenio de la puntuación z de estadística básica, y aquí no rige. La "
                "estandarización, cuando hace falta, se dice con palabras."),
             op("<em>Z</em>(<em>s</em>) es el valor en el punto y <em>z</em>(<em>s</em>) el valor "
                "en toda el área.", False,
                "El soporte —punto o área— no se marca con la caja de la letra: se marca en el "
                "argumento, escribiendo <em>s</em> o una región."),
             op("Son intercambiables; la distinción es tipográfica.", False,
                "Si fueran intercambiables no habría forma de escribir «la varianza de <em>Z</em>» "
                "distinguiéndola de «la dispersión de los <em>z</em> observados», que son "
                "exactamente las dos cosas que el capítulo 1 necesita separar.")]),
]


# ---------------------------------------------------------------------
# BLOQUE B · capítulo 2
# ---------------------------------------------------------------------
BLOQUE_B = [
    preg("opcion", "cap2", 1,
         f"Los semiejes del WGS84 se diferencian en {c('elip_a_menos_b')}, y pasar del "
         f"WGS84 al datum Bogotá 1975 desplaza las coordenadas de un mismo punto "
         f"{c('elip_datum_desp')} de media. ¿Qué es un datum?",
         "El punto no se mueve. ¿Qué se mueve entonces?",
         opciones=[
             op("La elección de elipsoide más su anclaje a la Tierra: cambiarlo cambia las "
                "coordenadas de un punto que no se ha movido.", True,
                "Por eso esa diferencia no es un error de medición: son dos formas "
                "de nombrar el mismo sitio. Ignorarlo mete esa distancia en los datos sin que "
                "nada falle."),
             op("La proyección con la que se dibuja el mapa.", False,
                "La proyección viene después y es otra decisión: primero se fija sobre qué figura y "
                "con qué anclaje se dan las coordenadas, y luego cómo se aplasta esa figura."),
             op("La unidad en la que se expresan las coordenadas.", False,
                "Grados o metros es una consecuencia del sistema elegido, no lo que lo define. Dos "
                "datums distintos pueden dar los dos en grados y no coincidir."),
             op("El origen del sistema de coordenadas de la hoja impresa.", False,
                "Eso es el marco del mapa. El datum es anterior al papel: existe aunque nadie "
                "dibuje nada.")]),

    preg("numerica", "cap2", 2,
         f"¿Cuántos metros mide un grado de longitud a la latitud de Bogotá "
         f"({n(N2['lat'], 3)}°), medido sobre el elipsoide WGS84? Da el valor en metros, "
         f"con un decimal.",
         "Un grado de longitud se acorta con el coseno de la latitud, y el radio que hay que "
         "usar es el de curvatura primo vertical.",
         respuesta=float(N2["correcto"]), tolerancia=5.0,
         retroAcierto=f"{n(N2['correcto'], 1)}&nbsp;m. En el ecuador serían "
                      f"{n(val('grad_lon_elip')[0], 1)}&nbsp;m, que es el máximo: el grado de "
                      f"longitud se acorta con el coseno de la latitud y sigue encogiendo hasta "
                      f"valer cero en el polo.",
         retroFallo=f"Son {n(N2['correcto'], 1)}&nbsp;m, y cada respuesta equivocada tiene "
                    f"nombre. Si te salió {dist(N2, 's2_esfera')}, es lo que devuelve "
                    f"<code>st_distance()</code> tal cual: en este entorno <code>sf</code> usa "
                    f"s2, que mide sobre una <strong>esfera</strong>, y su diferencia con el "
                    f"elipsoide es de {n(N2['dif_s2_m'], 1)}&nbsp;m por grado — mide de menos. "
                    f"Si te salió "
                    f"{dist(N2, 'olvida_coseno')}, olvidaste el coseno de la latitud y publicaste "
                    f"el grado del ecuador. Y si te salió {dist(N2, 'radio_meridional')}, usaste "
                    f"el radio meridional <em>M</em> en vez del primo vertical <em>N</em>."),

    preg("grafico", "cap2", 3,
         "El gráfico compara seis proyecciones por la <strong>razón de área máxima</strong> "
         "que introducen: cuántas veces se agranda la zona más distorsionada respecto de la "
         "menos distorsionada. ¿Qué se lee?",
         "Dos de las seis conservan los ángulos. Mira dónde caen respecto de las dos que "
         "conservan el área.",
         alto=240,
         descripcionGrafico="Barras de la razón de área máxima de seis proyecciones: las dos "
                            "equivalentes —Mollweide y Equal Earth— casi sin distorsión, "
                            "Robinson algo por encima de ellas, las dos conformes —Mercator y "
                            "Web Mercator— un orden de magnitud más arriba, y la azimutal "
                            "equidistante por encima de todas",
         dibujar="""canvas => {
            const g = DATOS_PRE1.graficos.g_proyecciones;
            return crearGraficoBarras(canvas, g.nombre, g.razon_max,
              { etiqueta: 'Razón de área máxima', tituloX: 'Proyección' });
          }""",
         opciones=[
             op("Que las dos proyecciones que conservan los ángulos deforman el área mucho más "
                "que las dos que la conservan.", True,
                "Es el intercambio que define a una proyección conforme: la distorsión angular "
                "media de Mercator es prácticamente cero, y lo paga en área. La barra más alta, "
                "eso sí, no es suya: es la azimutal equidistante, que no conserva ángulos ni "
                "áreas sino distancias desde un punto. Destruir el área no es cosa solo de las "
                "conformes — es el precio de conservar cualquier otra cosa."),
             op("Que Mercator es la peor proyección de las seis.", False,
                "«Peor» no significa nada sin decir para qué: para navegar trazando rumbos "
                "constantes es la que hay que usar, y para un mapa de coropletos es la que no. "
                "Y en área, mírala bien, Mercator no es siquiera la barra más alta."),
             op("Que las proyecciones con menos distorsión de área son las más exactas.", False,
                "Son las más exactas <em>en área</em>, y a cambio deforman ángulos y formas. Ninguna "
                "proyección es conforme y equivalente a la vez: es un resultado, no una limitación "
                "de las que hay disponibles."),
             op("Que la distorsión depende sobre todo del tamaño del área representada.", False,
                "Todas las barras se miden sobre el mismo mundo. Lo que cambia entre ellas es la "
                "proyección, no la extensión.")]),

    preg("opcion", "cap2", 4,
         f"Para los municipios continentales de Colombia, el error de área con EPSG:3116 "
         f"llega como máximo al {c('epsg_3116_max')} y con EPSG:9377 al "
         f"{c('epsg_9377_max')}. Pero las medianas van al revés: {c('epsg_3116_med')} con "
         f"3116 y {c('epsg_9377_med')} con 9377. Vas a publicar un mapa de áreas de todo el "
         f"país. ¿Cuál eliges y por qué?",
         "¿Qué municipio decide si un mapa nacional está bien: el típico o el peor?",
         opciones=[
             op("EPSG:9377, porque acota el peor caso, que es el que rompe un mapa nacional.", True,
                "En un mapa que cubre el país entero, la cifra que hay que poder defender es la del "
                "municipio peor representado. 9377 está pensado para eso: es el origen único "
                "nacional."),
             op("EPSG:3116, porque su mediana es mejor.", False,
                "La mediana premia al municipio típico, y los municipios pequeños son mayoría. Pero "
                "nadie audita un mapa nacional por su municipio mediano: lo audita por el que se ve "
                "mal, y ahí 3116 es peor."),
             op("EPSG:4326, porque es el estándar y evita reproyectar.", False,
                "4326 son grados: no es un sistema proyectado y calcular áreas ahí da grados "
                "cuadrados, que no son superficie. Es el error del módulo 10."),
             op("EPSG:3857, porque es lo que usan los mapas web.", False,
                "Web Mercator distorsiona el área con la latitud y no se diseñó para medir. Sirve "
                "para teselas de fondo, no para el cálculo que sostiene el mapa.")]),

    preg("multiple", "cap2", 5,
         f"Sobre las mismas {c('etiq_n_localidades')} localidades: <code>st_set_crs()</code> "
         f"desplaza los vértices "
         f"{c('etiq_set_crs')}; un <code>st_transform()</code> de verdad los desplaza hasta "
         f"{c('etiq_transform')}; y un <code>st_transform()</code> de EPSG:4686 a EPSG:4326 "
         f"los desplaza {c('etiq_silencioso')}. Marca <strong>todo</strong> lo cierto.",
         "Fíjate en que hay dos operaciones distintas que desplazan cero. Son dos.",
         opciones=[
             op("<code>st_set_crs()</code> no mueve ningún vértice: solo cambia la etiqueta.", True,
                "Reetiquetar es decir «estas coordenadas estaban en este sistema». Si la afirmación "
                "es falsa, los números se quedan y el significado se rompe."),
             op("Un desplazamiento de cero no prueba que la operación fuera correcta.", True,
                "Justo lo que muestra el caso 4686 → 4326: es una reproyección legítima entre datums "
                "compatibles y también da cero. Cero puede significar «no hice nada» o «no había "
                "nada que hacer», y desde el resultado no se distinguen."),
             op("<code>st_transform()</code> siempre mueve los vértices.", False,
                "El caso 4686 → 4326 los deja donde estaban. Usar el desplazamiento como prueba de "
                "que se reproyectó es la regla que este ejemplo desmonta."),
             op("Si el mapa se ve bien después, el CRS estaba bien puesto.", False,
                "Un CRS mal etiquetado da un mapa perfectamente creíble: los puntos guardan sus "
                "posiciones relativas. Lo que sale mal son las distancias, las áreas y los cruces "
                "con otras capas, y eso no se ve mirando.")],
         retroAcierto="Cero desplazamiento es compatible con haber hecho lo correcto y con no "
                      "haber hecho nada, y desde el resultado no se distinguen.",
         retroFallo="Se sostienen que <code>st_set_crs()</code> solo cambia la etiqueta y que un "
                    "desplazamiento de cero no prueba nada. Las otras dos usan el desplazamiento "
                    "como certificado, que es lo que el caso 4686 → 4326 desmonta."),

    preg("opcion", "cap2", 6,
         f"Si se miden distancias como si un grado fueran siempre "
         f"{n(D['nuevo']['euclidea_grados']['km_por_grado'], 4)}&nbsp;km, sobre los "
         f"{ent(D['nuevo']['euclidea_grados']['n_pares'])} pares de estaciones del IDEAM el "
         f"error medio es {cn('euclidea_grados.error_med_pct')}, el peor "
         f"{cn('euclidea_grados.error_max_pct')} y el método se pasa en el "
         f"{cn('euclidea_grados.pct_sobreestima')} de los pares. ¿Cuál es la consecuencia "
         f"que importa?",
         "Fíjate menos en el tamaño del error y más en su signo.",
         opciones=[
             op("Que al ser siempre por exceso, el error no se cancela al promediar muchas "
                "distancias: se acumula.", True,
                "Es lo que distingue un error de medida de un sesgo. Una fracción de punto en una "
                "distancia suelta es despreciable; esa misma fracción en la misma dirección en todas las "
                "distancias de un análisis corre el resultado entero."),
             op("Que el error es pequeño y en la práctica se puede ignorar.", False,
                "Sería defendible si el error fuera aleatorio. No lo es: apunta siempre al mismo "
                "lado, así que promediar no lo diluye, lo consolida."),
             op("Que el problema desaparece si las estaciones están cerca unas de otras.", False,
                "El error relativo no depende de la separación sino de la latitud: un grado de "
                "longitud vale menos cuanto más lejos del ecuador, y eso pesa igual en pares "
                "próximos."),
             op("Que hay que reproyectar a un sistema métrico antes de restar coordenadas.", False,
                "Es un buen consejo y resuelve el caso, pero no es lo que estas cifras miden. Aquí "
                "lo medido es la forma del error, y esa es la lección que sobrevive cuando "
                "reproyectar no es una opción.")]),

    preg("multiple", "cap2", 7,
         f"Guardando {c('form_n_rasgos')} rasgos en tres formatos: el shapefile trunca "
         f"{c('form_campos_largos')} nombres de campo a diez caracteres y convierte los "
         f"campos lógicos en {c('form_logico')}; el GeoPackage pesa "
         f"{c('form_gpkg_razon')}&nbsp;veces el shapefile y el GeoJSON "
         f"{c('form_geojson_razon')}. "
         f"Marca <strong>todo</strong> lo cierto.",
         "Son dos, y las dos son pérdidas de información, no de espacio.",
         opciones=[
             op("El shapefile trunca los nombres de campo a diez caracteres.", True,
                f"Y lo hace en silencio: {c('form_campos_largos')} de las "
                f"{c('form_n_campos')} columnas cambiaron de nombre sin un aviso, y el guion que "
                "las lea después por su nombre largo no encuentra nada."),
             op("El shapefile pierde el tipo lógico: lo guarda como entero.", True,
                "Un <code>TRUE</code> vuelve como <code>1</code>. Cualquier condición escrita contra "
                "el tipo original deja de comportarse igual, y tampoco avisa."),
             op("El GeoPackage pesa mucho más que el shapefile.", False,
                f"Pesa {c('form_gpkg_razon')}&nbsp;veces el shapefile: apenas más, y a cambio "
                f"conserva "
                f"los nombres y los tipos en un solo archivo. El GeoJSON sí es el pesado, "
                f"con {c('form_geojson_razon')}&nbsp;veces."),
             op("El GeoJSON es el formato más compacto de los tres.", False,
                "Es el más voluminoso con diferencia: es texto, y las coordenadas ocupan mucho "
                "escritas en decimal.")],
         retroAcierto="Lo que descalifica al shapefile no es el tamaño: es lo que pierde sin "
                      "decirlo, y las dos pérdidas son de información.",
         retroFallo="Se sostienen las dos pérdidas del shapefile —los nombres de campo y el tipo "
                    "lógico—. Las otras dos hablan de tamaño, que es justo la parte en la que el "
                    "shapefile gana."),

    preg("opcion", "cap2", 8,
         f"Al construir un objeto <code>sf</code> desde un CSV con las columnas en el orden "
         f"equivocado, los puntos se desplazan {c('csv_desplaz_med')} de media, "
         f"{c('csv_en_colombia')} de las {cn('euclidea_grados.n_estaciones')} estaciones "
         f"caen dentro de Colombia y "
         f"<code>sf</code> avisó: {c('csv_hubo_aviso')}. ¿Cuál es la comprobación mínima "
         f"antes de seguir?",
         "El error no está en el CRS ni en los datos: está en qué columna se leyó como qué.",
         opciones=[
             op("Mirar la caja envolvente, o pintar los puntos, antes de hacer nada más.", True,
                "Dos segundos y un vistazo. Una caja cuyos valores de longitud rondan el 5 y los de "
                "latitud el −70 delata el intercambio de inmediato, y ninguna otra comprobación "
                "automática lo iba a hacer."),
             op("Confiar en que <code>sf</code> avisa si algo no cuadra.", False,
                "No avisó, y no puede: −74 y 4 son una longitud y una latitud perfectamente válidas "
                "cada una por su lado. La biblioteca no sabe dónde esperabas que cayera el punto."),
             op("Comprobar que el EPSG es el correcto.", False,
                "El EPSG era correcto. Ese es el detalle incómodo: se puede tener el sistema de "
                "referencia bien puesto y las coordenadas cambiadas de sitio."),
             op("Reproyectar a EPSG:9377, que es el sistema nacional.", False,
                "Reproyectar un punto que está en el sitio equivocado lo lleva, con toda precisión, "
                "al sitio equivocado en otro sistema.")]),

    preg("opcion", "cap2", 9,
         f"Geocodificando las sedes educativas de Bogotá, la tasa global de asignación "
         f"errónea de localidad es del {c('pos_tasa_global')}. Pero entre la localidad peor "
         f"y la mejor hay un factor de {c('pos_razon_max_min')}, y la tasa correlaciona "
         f"{c('pos_corr')} con lo poco compacta que es la localidad. ¿Qué añade el desglose "
         f"que la cifra global escondía?",
         "Una tasa global es una media. ¿Sobre qué se está promediando?",
         opciones=[
             op("Que el error no se reparte por igual: hay localidades muchísimo peor servidas "
                "que otras, y no al azar.", True,
                "Una tasa global de ese orden suena a ruido tolerable. Deja de sonar así cuando se "
                "sabe que se "
                "concentra en localidades con una forma determinada, porque entonces cualquier "
                "análisis por localidad hereda ese sesgo."),
             op("Que la tasa global está mal calculada.", False,
                "Está bien calculada: es la media real. El problema no es que mienta, es que una "
                "media no dice nada sobre cómo se reparte lo que promedia."),
             op("Que hace falta una fuente de direcciones mejor.", False,
                "Puede que sí, pero no es lo que estas cifras muestran. La correlación con la "
                "compacidad apunta a la geometría de las zonas, no a la calidad de las direcciones."),
             op("Que el error posicional es irrelevante si la tasa global es baja.", False,
                "Una tasa global baja dice que el error es raro, no que sea inofensivo. Si se "
                "repartiera al azar, promediar lo diluiría; concentrado en localidades de una "
                "forma determinada, cualquier comparación entre localidades hereda ese sesgo y "
                "lo lee como diferencia real.")]),

    preg("opcion", "cap2", 10,
         f"Un polígono con una autointersección declara un área de {c('topo_area_antes')} y, "
         f"tras <code>st_make_valid()</code>, de {c('topo_area_despues')}. Un buffer de "
         f"radio 1 000 construido sobre coordenadas en grados da "
         f"{c('topo_buffer_grados')}, cuando el mismo buffer bien hecho mide "
         f"{c('topo_buffer_3857')}. ¿Qué tienen en común los dos casos?",
         "¿Cuál de las dos operaciones lanzó un error?",
         opciones=[
             op("Que las dos devuelven un número en vez de fallar, y ese número parece una medida.",
                True,
                "Un área de cero y un área ridículamente pequeña son resultados, no "
                "excepciones. Nada en el flujo se detiene, y lo que sigue trabaja con ellos como si "
                "fueran superficies."),
             op("Que las dos se arreglan con <code>st_make_valid()</code>.", False,
                "<code>st_make_valid()</code> arregla la topología del primero. No tiene nada que "
                "decir sobre el segundo, que es geométricamente válido: lo que está mal son las "
                "unidades."),
             op("Que las dos vienen de datos de mala calidad.", False,
                "El segundo caso parte de datos impecables. El error lo introduce la operación, al "
                "aplicar un radio en metros sobre coordenadas en grados."),
             op("Que las dos producen un aviso en consola que conviene leer.", False,
                "Ese es el problema: no lo producen. Si lo hicieran, ninguno de los dos sería "
                "interesante como trampa.")]),

    preg("numerica", "cap2", 11,
         f"Cruzar {c('ing_pares_bruta')} pares por fuerza bruta se reduce a "
         f"{c('ing_pares_cajas')} tras el filtro de cajas envolventes del índice espacial. "
         f"¿Cuántas veces menos trabajo es? Da dos decimales.",
         "Divide los pares de antes entre los de después.",
         respuesta=float(val("ing_reduccion")), tolerancia=0.2,
         retroAcierto=f"{c('ing_reduccion')}. Y el filtro de cajas es solo el primer paso: "
                      f"descarta lo imposible barato para que la comprobación geométrica cara se "
                      f"haga sobre una fracción de ellos.",
         retroFallo=f"Son {c('ing_reduccion')}. El orden importa: si te salió "
                    f"{dist(N6, 'al_reves')}, dividiste al revés, y eso es la fracción de "
                    f"trabajo que queda. Si te salió {dist(N6, 'olvida_el_resto')}, contaste "
                    f"los pares que se ahorran y olvidaste los que quedan por comparar: el "
                    f"trabajo no baja a cero. Y {dist(N6, 'pct_reduccion')} es el porcentaje "
                    f"en que se reduce, que describe el mismo hecho y no es el mismo número. "
                    f"La cifra que hay que retener es que el "
                    f"índice no cambia el resultado del <em>join</em>, solo el trabajo que "
                    f"cuesta llegar a él."),
]

# ---------------------------------------------------------------------
# BLOQUE C · capítulo 3, módulos 1 a 8
# ---------------------------------------------------------------------
BLOQUE_C = [
    preg("opcion", "cap3", 1,
         f"Sobre la deserción municipal, {c('c3m1_config')} combinaciones de esquema y de "
         f"<em>k</em> producen {c('c3m1_distintos')} mapas visualmente distintos —el "
         f"{c('c3m1_pct')} de ellas— y {c('c3m1_vacias')} dejan alguna clase sin un solo "
         f"municipio. El dato es el mismo en todas. ¿Qué se sigue de ahí?",
         "El dato no cambia en ninguna de esas combinaciones. ¿Qué cambia entonces?",
         opciones=[
             op("Que el mapa no es el dato: entre los dos hay decisiones que el mapa no "
                "declara.", True,
                "El esquema y el <em>k</em> son parámetros de quien dibuja, no propiedades de la "
                "deserción. Por eso el capítulo exige publicarlos <em>junto</em> al mapa: sin "
                "ellos, quien lo lee no puede saber qué está viendo."),
             op("Que hay que probar varios esquemas y quedarse con el que mejor se vea.", False,
                "Elegir por apariencia es el procedimiento que garantiza obtener el mapa que uno "
                "ya quería. La elección se justifica por la forma de la distribución y por la "
                "pregunta que el mapa contesta, y se declara."),
             op("Que la clasificación por cuantiles es la única defendible, porque reparte los "
                "municipios por igual.", False,
                "Repartir por igual no es ser neutral: con una distribución asimétrica, los "
                "cuantiles juntan en una misma clase valores muy separados y separan valores "
                "casi idénticos. Es una decisión más, con sus consecuencias."),
             op("Que el dato de deserción es demasiado ruidoso para cartografiarlo.", False,
                "El dato no se ha tocado en ninguna de las combinaciones. Lo que varía es la "
                "partición que se le impone desde fuera; culpar al dato es atribuirle una "
                "decisión que no tomó él.")]),

    preg("multiple", "cap3", 2,
         f"Sobre los mismos municipios, el conteo de estudiantes y el puntaje medio "
         f"correlacionan {c('c3m2_r')} por Pearson y {c('c3m2_rho')} por Spearman; de los 20 "
         f"primeros por cada criterio solo {c('c3m2_solape')} municipio aparece en las dos "
         f"listas; y los diez municipios con más estudiantes —el {c('c3m2_pct_mun')} "
         f"del país— concentran el {c('c3m2_pct_est')} de ellos. Marca "
         f"<strong>todo</strong> lo cierto.",
         "Son dos. Pregúntate qué pregunta contesta cada uno de los dos mapas.",
         opciones=[
             op("Un mapa de conteos y uno de tasas contestan preguntas distintas, y ninguno "
                "sustituye al otro.", True,
                "El conteo dice dónde está la gente; la tasa, cómo le va. Que sus ordenamientos "
                "apenas se solapen no es una contradicción: es la prueba de que no miden lo mismo."),
             op("Un coropleto de conteos dibuja sobre todo dónde vive la población.", True,
                "Con los estudiantes concentrados como lo están, el mapa de conteos reproduce el "
                "mapa de población y le pone encima el rótulo de otra variable. Es el «normalizar "
                "o mentir» del módulo, ocurriendo."),
             op("Como la correlación es casi nula, uno de los dos ordenamientos está mal "
                "calculado.", False,
                "Los dos están bien calculados, y el Spearman lo confirma sobre los rangos. Que "
                "dos resúmenes del mismo dato no correlacionen es información sobre el dato, no "
                "el síntoma de un error de cálculo."),
             op("La tasa es siempre preferible al conteo para cualquier mapa.", False,
                "No: para dimensionar una intervención o repartir recursos hace falta el conteo, "
                "porque los recursos se gastan en personas y no en proporciones. La regla no es "
                "«usa tasa», es «di cuál usas y por qué».")],
         retroAcierto="No hay un mapa correcto y otro incorrecto: hay dos preguntas, y cada "
                      "mapa contesta la suya.",
         retroFallo="Se sostienen que los dos mapas contestan preguntas distintas y que el de "
                    "conteos dibuja la población. Las otras dos convierten un hallazgo sobre el "
                    "dato en un error de cálculo, o una recomendación en una regla."),

    preg("numerica", "cap3", 3,
         f"Clasificando SID74 por cuantiles con <em>k</em> = 5, los cortes son "
         f"{', '.join(ent(x) for x in val('c3m3_cortes'))}. La primera clase se lleva "
         f"{cn('convenio_intervalo.primera_clase_r')} condados en R y "
         f"{cn('convenio_intervalo.primera_clase_python')} en Python, con el mismo dato y el "
         f"mismo esquema. ¿Cuántos condados cambia de sitio esa diferencia de convenio?",
         "No hay que recalcular nada: la respuesta está en las dos cifras que da el "
         "enunciado.",
         respuesta=float(val_nuevo("convenio_intervalo.movidos_primera")), tolerancia=0.5,
         retroAcierto=f"{cn('convenio_intervalo.movidos_primera')} condados. R cierra el "
                      f"intervalo por {c('c3m3_convenio_r')} y Python por "
                      f"{c('c3m3_convenio_py')}: los que valen justo el corte caen a un lado "
                      f"o al otro según el programa.",
         retroFallo=f"Son {cn('convenio_intervalo.movidos_primera')}. Si contestaste "
                    f"{dist(N3, 'ninguno')}, diste por hecho que «clasificación por cuantiles» "
                    f"significa exactamente lo mismo en los dos programas. Si contestaste "
                    f"{dist(N3, 'primera_clase_r')}, diste el tamaño de la primera clase en R "
                    f"y no la diferencia entre las dos. Y si contestaste "
                    f"{dist(N3, 'todos_los_empates')}, contaste los condados empatados en "
                    f"cualquiera de los cinco cortes, cuando la pregunta es por los que se "
                    f"mueven en el primero. Significa lo mismo salvo por el lado cerrado "
                    f"del intervalo, y con {c('c3m3_empatados')} condados empatados justo en "
                    f"un corte eso basta para publicar dos mapas distintos con el mismo pie."),

    preg("grafico", "cap3", 4,
         "El gráfico mide, para cada par de esquemas de clasificación, qué porcentaje de "
         "municipios cambia de clase al pasar de uno al otro. Los diez pares salen de los cinco "
         "esquemas del módulo —intervalos iguales, cuantiles, Fisher-Jenks, desviación estándar "
         "y head/tails—, sobre el mismo dato y el mismo <em>k</em>. ¿Qué se lee?",
         "Compara la barra más alta con la más baja, y fíjate en que ninguna es cero.",
         alto=300,
         descripcionGrafico=f"Barras del porcentaje de municipios que cambian de clase en cada "
                            f"uno de los diez pares que forman los cinco esquemas de "
                            f"clasificación —intervalos iguales, cuantiles, Fisher-Jenks, "
                            f"desviación estándar y head/tails—: la barra más alta llega al "
                            f"{c('c3m4_discordante')}, la más baja al {c('c3m4_concordante')}, "
                            f"y ninguna es cero",
         # Los rótulos van abreviados y en dos líneas, y el enunciado los
         # nombra enteros. Con los nombres completos, diez pares en un lienzo
         # de este ancho salen rotados y solapados: el gráfico se vuelve
         # ilegible justo en la parte que hay que leer.
         dibujar="""canvas => {
            const g = DATOS_PRE1.graficos.g_discordancia;
            const corto = { 'Intervalos iguales': 'Iguales', 'Fisher-Jenks': 'Fisher',
                            'Desviación estándar': 'Desv. est.' };
            const rotulos = g.etiqueta.map(
              s => s.split(' / ').map(x => corto[x] || x));
            return crearGraficoBarras(canvas, rotulos, g.pct,
              { etiqueta: '% de municipios que cambian de clase',
                tituloX: 'Par de esquemas comparados' });
          }""",
         opciones=[
             op("Que cambiar de esquema puede recolorear a la mayoría de los municipios, y "
                "cuánto depende de qué dos esquemas se comparen.", True,
                f"Del par más discordante ({c('c3m4_discordante')}) al más concordante "
                f"({c('c3m4_concordante')}) hay un abismo, y solo el {c('c3m4_estables')} de "
                f"los municipios se queda en su clase con todos los esquemas. Un mismo "
                f"municipio llega a tomar {c('c3m4_rango_max')} clases distintas."),
             op("Que los esquemas que más se parecen entre sí son los más correctos.", False,
                "Parecerse no es acertar. Dos esquemas pueden coincidir porque los dos aplanan "
                "la misma cola de la distribución, y coincidirían igual estando los dos mal "
                "elegidos para la pregunta. La concordancia mide estabilidad, no validez."),
             op("Que el efecto es pequeño, porque ninguna barra llega al 100 %.", False,
                f"El par más discordante mueve de clase al {c('c3m4_discordante')} de los "
                f"municipios. Un mapa en el que esa proporción cambia de color no es una "
                f"variante del anterior: es otro mapa."),
             op("Que conviene quedarse con el par de esquemas más concordante.", False,
                "Un par no se usa: se publica un mapa, con un esquema. El gráfico no propone "
                "parejas, mide cuánto depende el mapa de una decisión que casi nunca se declara "
                "en el pie.")]),

    preg("numerica", "cap3", 5,
         f"En visión típica, la distancia perceptual entre el rojo y el verde de una paleta "
         f"vale {c('c3m5_dE_normal')}; simulando deuteranopia sobre esos mismos dos colores "
         f"baja a {c('c3m5_dE_deuter')}. ¿En qué porcentaje cae? Da dos decimales.",
         "Es la caída relativa respecto del valor de partida, no la diferencia a secas.",
         respuesta=float(val("c3m5_caida")), tolerancia=1.0,
         retroAcierto=f"{c('c3m5_caida')}. Dos colores que en la pantalla de quien hace el "
                      f"mapa son opuestos llegan a una parte de sus lectores como el mismo "
                      f"color.",
         retroFallo=f"Es {c('c3m5_caida')}. Si te salió {dist(N8, 'lo_que_queda')}, diste el "
                    f"porcentaje que QUEDA en vez del que se pierde. Si te salió "
                    f"{dist(N8, 'diferencia')}, diste la caída en unidades de distancia "
                    f"perceptual y no en porcentaje. Y si te salió "
                    f"{dist(N8, 'base_deuteranopia')}, dividiste por la distancia bajo "
                    f"deuteranopia en vez de por la de partida: se cae DESDE la visión típica, "
                    f"así que la base es ella. Y la cifra "
                    f"suelta no es el argumento: el módulo simula {c('c3m5_comparaciones')} "
                    f"comparaciones de color, porque lo que hay que poder defender no es un par "
                    f"de colores sino la paleta entera."),

    preg("opcion", "cap3", 6,
         f"<code>tmap</code> {c('c3m6_version')} construye un mapa encadenando verbos —el "
         f"material verifica {c('c3m6_verbos')} ejecutándolos—: <code>tm_shape()</code> "
         f"declara el dato, <code>tm_polygons()</code> cómo se pinta, "
         f"<code>tm_scale_intervals()</code> cómo se clasifica y <code>tm_layout()</code> cómo "
         f"se compone. ¿Qué gana el mapa por escribirse así?",
         "Fíjate en qué queda escrito y, por tanto, en qué queda disponible para discutirse.",
         opciones=[
             op("Que cada decisión cartográfica ocupa una línea propia, y por eso se puede "
                "revisar, discutir y repetir.", True,
                "Es lo que aporta una gramática frente a una función con veinte argumentos: el "
                "esquema, el <em>k</em> y la paleta dejan de estar enterrados en valores por "
                "defecto y pasan a ser verbos que alguien puede leer."),
             op("Que el mapa sale más bonito que con la función de dibujo de <code>sf</code>.",
                False,
                "Las cosas por defecto están mejor elegidas, es verdad, y no es lo que la "
                "gramática aporta. Un mapa bonito con un esquema sin declarar sigue sin poder "
                "revisarse."),
             op("Que el paquete elige por ti el esquema de clasificación adecuado.", False,
                "Elige uno por defecto, que no es lo mismo que el adecuado. Aceptar el valor por "
                "defecto es una decisión tan cartográfica como cualquier otra, y la gramática la "
                "deja a la vista en vez de esconderla."),
             op("Que evita tener que preocuparse por el sistema de referencia de la capa.", False,
                "Puede reproyectar al vuelo para dibujar, y eso no arregla nada si el CRS estaba "
                "mal <em>puesto</em>: se vería igual de bien y seguiría midiendo mal. Dibujar y "
                "medir siguen siendo dos cosas distintas.")]),

    preg("multiple", "cap3", 7,
         f"Del mismo dato departamental salen tres representaciones que no son un coropleto: "
         f"un mapa de densidad de puntos donde cada punto vale {c('c3m7_por_punto')} "
         f"estudiantes ({c('c3m7_n_puntos')} puntos en total), un hexbin de "
         f"{c('c3m7_hexagonos')} celdas y unos símbolos proporcionales cuyo valor mayor es "
         f"{c('c3m7_razon_simbolos')} el menor. Marca <strong>todo</strong> lo cierto.",
         "Son dos. Piensa en qué distorsiona el área de la unidad y qué trae de propina cada "
         "alternativa.",
         opciones=[
             op("En un coropleto, una unidad grande pesa más en la vista aunque tenga menos "
                "gente.", True,
                "El ojo suma superficie, no valor, y esa es la razón de existir de todas las "
                "alternativas del módulo: romper la asociación entre extensión e importancia."),
             op("En un mapa de densidad de puntos, la posición exacta de cada punto no "
                "significa nada.", True,
                "Los puntos se reparten dentro de la unidad. Lo que informa es cuántos hay y "
                "cómo se concentran; leer dónde cae uno concreto es leer el dibujo, no el dato."),
             op("Los símbolos proporcionales resuelven el problema, porque el área del círculo "
                "es proporcional al valor.", False,
                "Resuelven el sesgo del área de la unidad y traen el suyo: con esa razón entre "
                "el valor mayor y el menor, el círculo grande se come a sus vecinos y el pequeño "
                "desaparece."),
             op("El hexbin es preferible siempre, porque todas sus celdas tienen la misma área.",
                False,
                "La igualdad de área es una ventaja real y una pérdida real a la vez: desaparecen "
                "las fronteras administrativas, que son las unidades sobre las que alguien decide. "
                "Es un cambio de soporte, no una mejora gratis.")],
         retroAcierto="Cada alternativa arregla un sesgo del coropleto y aporta el suyo; "
                      "ninguna es la respuesta correcta por sí sola.",
         retroFallo="Se sostienen el sesgo del área de la unidad y la falta de significado de la "
                    "posición de un punto suelto. Las otras dos presentan como solución lo que "
                    "es un intercambio."),

    preg("grafico", "cap3", 8,
         "El gráfico traza la correlación media entre educación de la madre y puntaje según en "
         "cuántas zonas se agregue a los mismos estudiantes, con la línea de puntos en el "
         "valor calculado sobre estudiantes individuales. ¿Qué se lee?",
         "Mira hacia qué lado del gráfico se acerca la curva a la línea de puntos, y hacia "
         "cuál se aleja.",
         alto=250,
         descripcionGrafico="Curva de la correlación media según el número de zonas de "
                            "agregación: muy por encima de la línea del valor individual con "
                            "pocas zonas, y por debajo de ella con muchas",
         dibujar="""canvas => {
            const g = DATOS_PRE1.graficos.g_escala;
            const ind = DATOS_PRE1.reutilizado.c3m8_r_ind.valor;
            return crearGraficoLinea(canvas, g.zonas.map(x => String(x)), [
              { label: 'Correlación media entre zonas', data: g.media,
                borderColor: COLORES_GRAFICO.primario, backgroundColor: 'transparent',
                tension: 0.25, pointRadius: 3, borderWidth: 2 },
              { label: 'Sobre estudiantes individuales', data: g.zonas.map(() => ind),
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent',
                borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5 }
            ]);
          }""",
         opciones=[
             op("Que el valor depende de en cuántas zonas se agregue: con pocas queda muy "
                "por encima del individual y con muchas se le acerca hasta caer por debajo.",
                True,
                f"Con pocas zonas se promedia dentro de cada una y desaparece la variación entre "
                f"individuos, que es la que tiraba de la correlación hacia abajo; con muchas "
                f"zonas queda poca gente en cada una y aparece el ruido de las medias pequeñas. "
                f"Sobre los 33 departamentos reales el valor es {c('c3m8_r_dep')}, frente a "
                f"{c('c3m8_r_ind')} sobre estudiantes: es el efecto escala del MAUP."),
             op("Que la correlación verdadera es la de las zonas grandes, porque tiene menos "
                "ruido.", False,
                "«Menos ruido» y «más cerca de la verdad» no son lo mismo. Lo que se ha quitado "
                "al promediar es variación real entre personas, no error de medida; el número "
                "que sale es correcto para las zonas, y no es una estimación mejor del valor "
                "individual."),
             op("Que hace falta aumentar el número de repeticiones por escala para estabilizar "
                "la curva.", False,
                "El número de repeticiones no es el problema. Con muchas zonas la curva ya es "
                "estable; con pocas, el resultado depende de verdad de cuáles sean esas zonas, y "
                "eso no se arregla repitiendo más: es el fenómeno que el módulo mide."),
             op("Que la relación entre educación de la madre y puntaje se refuerza al subir de "
                "escala.", False,
                "Lo que sube es un número calculado sobre otras unidades. La relación entre las "
                "personas no cambia porque alguien las agrupe: leer la subida como un "
                "«refuerzo» es atribuir al fenómeno lo que hizo la agregación.")]),
]
# ---------------------------------------------------------------------
# BLOQUE D · integración. Cada pregunta cruza al menos dos capítulos, y
# declara el módulo al que conviene volver PRIMERO, que no siempre es el
# del capítulo donde vive la cifra que cita.
# ---------------------------------------------------------------------
BLOQUE_D = [
    preg("opcion", "cap1", 2,
         f"Un mapa de densidad de puntos reparte los estudiantes de cada departamento en "
         f"puntos de {c('c3m7_por_punto')} estudiantes cada uno, {c('c3m7_n_puntos')} en "
         f"total. Alguien propone medir su agrupamiento con el índice de Clark-Evans, como se "
         f"hizo con las plántulas de secuoya. ¿Qué le contestas?",
         "Vuelve a la pregunta con la que abre el capítulo 1: ¿qué es aleatorio en este dato?",
         opciones=[
             op("Que ese índice mediría el reparto que hizo el programa al dibujar, no el de "
                "los estudiantes.", True,
                "Los puntos no son estudiantes localizados: son un recurso gráfico colocado "
                "dentro de cada departamento. El dato de partida es de área y lo sigue siendo, "
                "por mucho que el mapa se parezca a un patrón puntual."),
             op("Que basta con construir un <code>ppp</code> con la ventana del país y "
                "entonces sí vale.", False,
                "El objeto se construye sin protestar y el índice devuelve un número. Ese es "
                "exactamente el peligro: el procedimiento no falla, y lo que describe el "
                "resultado es el dibujo."),
             op("Que Clark-Evans solo funciona con patrones de pocos puntos.", False,
                "No hay tal límite: el índice está definido para cualquier número de puntos. Lo "
                "que descalifica el cálculo no es el tamaño del patrón, es de dónde salieron las "
                "posiciones."),
             op("Que primero hay que corregir el efecto de borde y luego el índice ya vale.", False,
                "La corrección de borde es necesaria y real cuando el dato <em>es</em> un patrón "
                "puntual. Aquí no arregla nada, porque el problema está un paso antes: las "
                "posiciones no las puso el fenómeno.")]),

    preg("grafico", "cap1", 6,
         f"El gráfico traza el variograma teórico de un proceso y, encima, lo que devuelven "
         f"{c('realiz_n')} realizaciones suyas: la media de todas ellas y la banda entre los "
         f"percentiles 5 y 95. ¿Qué se lee?",
         "Fíjate en cuánto se abre la banda a medida que crece el retardo, y en dónde cae la "
         "media.",
         alto=250,
         descripcionGrafico=f"Variograma teórico, media de {c('realiz_n')} realizaciones y "
                            f"banda entre los percentiles 5 y 95, que se ensancha conforme "
                            f"crece el retardo",
         dibujar="""canvas => {
            const g = DATOS_PRE1.graficos.g_variograma;
            const gris = { backgroundColor: 'transparent', pointRadius: 0, borderWidth: 1.5,
                           borderColor: COLORES_GRAFICO.gris };
            return crearGraficoLinea(canvas, g.lags.map(x => String(x)), [
              { label: 'Teórico', data: g.teorico, borderColor: COLORES_GRAFICO.primario,
                backgroundColor: 'transparent', borderDash: [6, 4],
                pointRadius: 0, borderWidth: 2 },
              { label: 'Media de las realizaciones', data: g.media,
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent',
                tension: 0.25, pointRadius: 3, borderWidth: 2 },
              Object.assign({ label: 'Percentil 5', data: g.q05 }, gris),
              Object.assign({ label: 'Percentil 95', data: g.q95 }, gris)
            ]);
          }""",
         opciones=[
             op("Que una sola realización puede quedar muy lejos del variograma del proceso, y "
                "tanto más cuanto mayor es el retardo.", True,
                "La banda dice lo que le puede pasar a una realización, y se abre conforme "
                "crece el retardo. Con un solo mapa —que es lo que siempre se tiene— se está en "
                "algún punto de esa banda, sin saber en cuál."),
             op("Que el estimador del variograma está sesgado en los retardos grandes.", False,
                "El sesgo que propone no está donde lo pone: en los retardos grandes la media "
                "de las realizaciones y el teórico van juntos, y lo que crece ahí es la "
                "dispersión —hay menos pares que promediar—, que es varianza y no sesgo. La "
                "única separación visible está en el retardo más corto, y tampoco es del "
                "estimador: cada retardo agrupa los pares que caen a media unidad de él, y en el "
                "primero eso mezcla los vecinos de al lado con los de la diagonal, que están "
                "más lejos."),
             op("Que el proceso deja de ser estacionario a partir de cierto retardo.", False,
                "El proceso simulado es estacionario por construcción. Confundir la apertura de "
                "la banda con una pérdida de estacionariedad es leer una propiedad del estimador "
                "como si fuera del proceso."),
             op("Que hacen falta más realizaciones para estabilizar la media.", False,
                "La media ya está estabilizada. El problema del capítulo 1 nunca fue cuántas "
                "realizaciones se simulan, sino que en la realidad se observa una.")]),

    preg("multiple", "cap2", 9,
         f"Las sedes educativas de Bogotá vienen geocodificadas. Al redondear sus coordenadas "
         f"a dos decimales quedan {c('pos_sedes_por_pos')} sedes por posición distinta, "
         f"mientras que la distancia mediana de una sede a su vecina más cercana es "
         f"{c('ing_vecino_mediana')}. Marca <strong>todo</strong> lo cierto.",
         "Son dos. Compara el tamaño del grano de la coordenada con la separación real entre "
         "sedes.",
         opciones=[
             op("Redondear a dos decimales borra la separación real entre sedes vecinas.", True,
                f"La centésima de grado a la que se redondea es un grano mucho más grueso que la "
                f"separación real: a la latitud de Bogotá un grado de longitud mide "
                f"{n(val('grad_lon_elip')[1], 1)}&nbsp;m, y la mediana entre sedes vecinas es "
                f"{c('ing_vecino_mediana')}. Al redondear, muchas caen en el mismo punto: no se "
                f"pierde precisión, se pierde el fenómeno."),
             op("Un análisis de patrón puntual sobre estas coordenadas mediría en parte el "
                "geocodificador.", True,
                "Si varias sedes comparten posición porque el geocodificador las llevó al mismo "
                "punto —el centroide de la manzana, del barrio, de la vía—, las distancias entre "
                "vecinos son las que produjo esa asignación."),
             op("El problema desaparece guardando las coordenadas con más decimales.", False,
                "Más decimales conservan lo que el geocodificador dijo, con toda su falsa "
                "precisión. El error posicional no está en cómo se guardan las coordenadas: "
                "está en cómo se obtuvieron."),
             op("Como el error posicional es de pocos metros, no afecta a un mapa por "
                "localidades.", False,
                "Afecta justo donde importa: en las sedes cercanas a un borde, que son las que "
                "cambian de localidad. Un error pequeño en todas partes se convierte en una "
                "asignación equivocada en la frontera.")],
         retroAcierto="La coordenada de una dirección geocodificada es una estimación, y "
                      "conviene tratarla como tal.",
         retroFallo="Se sostienen que el redondeo borra la separación real entre sedes y que un "
                    "análisis de patrón puntual mediría en parte al geocodificador. Las otras "
                    "dos buscan el problema en cómo se guardan las coordenadas, o lo dan por "
                    "pequeño."),

    preg("grafico", "cap2", 2,
         "El gráfico traza cuántos metros mide un grado de longitud sobre el elipsoide WGS84 "
         "según la latitud, con la línea de puntos en el valor que toma en el ecuador. ¿Qué se "
         "lee?",
         "Compara la curva con la línea de puntos en el extremo derecho del gráfico.",
         alto=250,
         descripcionGrafico="Curva descendente de los metros que mide un grado de longitud "
                            "conforme sube la latitud, con la línea de referencia del valor en "
                            "el ecuador",
         dibujar="""canvas => {
            const g = DATOS_PRE1.graficos.g_grado;
            return crearGraficoLinea(canvas, g.lat.map(x => String(x)), [
              { label: 'Metros por grado de longitud', data: g.elipsoide,
                borderColor: COLORES_GRAFICO.primario, backgroundColor: 'transparent',
                tension: 0.25, pointRadius: 3, borderWidth: 2 },
              { label: 'El valor del ecuador', data: g.lat.map(() => g.elipsoide[0]),
                borderColor: COLORES_GRAFICO.secundario, backgroundColor: 'transparent',
                borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5 }
            ]);
          }""",
         opciones=[
             op("Que convertir grados a metros con un factor fijo sobreestima la distancia en "
                "todas partes salvo en el ecuador, y cada vez más al subir en latitud.", True,
                f"La curva solo toca la línea de puntos en un extremo. Entre Bogotá y Oslo el "
                f"grado se acorta {c('grad_bogota_oslo')}, y sobre las estaciones del IDEAM la "
                f"diferencia entre medir bien y medir con un factor fijo llega a "
                f"{c('medir_dist_max')}."),
             op("Que el grado de latitud también se acorta al subir hacia el polo.", False,
                "El gráfico no dice nada de la latitud: la única curva que hay es la de la "
                "longitud. Y el grado de latitud hace lo contrario, alargarse, porque el "
                "elipsoide se curva menos cerca del polo."),
             op("Que el error importa poco, porque la curva es suave.", False,
                f"Suave no es pequeña: en el extremo derecho del gráfico un grado mide "
                f"{ent(val('grad_lon_elip')[10])}&nbsp;m frente a "
                f"{ent(val('grad_lon_elip')[0])}&nbsp;m en el ecuador. Que el cambio sea gradual "
                f"es justo lo que hace que no salte a la vista."),
             op("Que el problema se resuelve usando la esfera en vez del elipsoide.", False,
                "La esfera da una curva de la misma forma: el acortamiento con la latitud no "
                "viene de la figura de la Tierra, viene de que los meridianos convergen. Elegir "
                "superficie desplaza la curva; no la endereza.")]),

    preg("numerica", "cap3", 8,
         f"La correlación entre la educación de la madre y el puntaje vale {c('c3m8_r_ind')} "
         f"calculada sobre estudiantes y {c('c3m8_r_dep')} sobre las medias departamentales. "
         f"¿En qué porcentaje sube al agregar? Da dos decimales.",
         "Es la subida relativa respecto del valor calculado sobre estudiantes.",
         respuesta=float(val("c3m8_subida")), tolerancia=1.0,
         retroAcierto=f"{c('c3m8_subida')}. Y por el camino hay una sorpresa que conviene "
                      f"llevarse al parcial: a nivel municipal la correlación no sube, baja a "
                      f"{c('c3m8_r_mun')}. La agregación no empuja siempre en la misma "
                      f"dirección.",
         retroFallo=f"Es {c('c3m8_subida')}. Si te salió {dist(N9, 'base_departamento')}, "
                    f"tomaste como base la correlación agregada en vez de la individual: se "
                    f"sube DESDE el individuo. Si te salió {dist(N9, 'razon')}, diste la razón "
                    f"y no el incremento. Y si te salió {dist(N9, 'con_municipio')}, agregaste "
                    f"a municipio en vez de a departamento, donde la correlación no sube: baja, "
                    f"y el signo lo está diciendo. "
                    f"Agregar no mejora la medida: promedia dentro de "
                    f"cada unidad y se lleva la variación entre individuos, que es la que "
                    f"tiraba de la correlación hacia abajo. Solo el {c('c3m8_pct_var')} de la "
                    f"varianza total vive entre municipios; el resto está dentro de ellos, y la "
                    f"agregación lo borra. Es la misma operación que en el capítulo 1 hacía "
                    f"<em>bajar</em> el Moran I al pasar de municipio a departamento: lo que "
                    f"decide el signo es si lo que se promedia era señal o era ruido para lo "
                    f"que se está midiendo."),

    preg("multiple", "cap2", 11,
         f"Tienes un CSV de sedes con longitud y latitud y un GeoPackage de localidades en "
         f"EPSG:9377, y quieres publicar un coropleto de sedes por cada mil habitantes. El "
         f"cruce espacial son {c('ing_pares_bruta')} pares por fuerza bruta. Marca "
         f"<strong>todo</strong> lo que hay que hacer <strong>antes</strong> de clasificar y "
         f"pintar.",
         "Son dos. Piensa en qué paso, si se salta, devuelve un número equivocado sin avisar.",
         opciones=[
             op("Llevar las dos capas al mismo CRS con <code>st_transform()</code>, no con "
                "<code>st_set_crs()</code>.", True,
                "<code>sf</code> se planta si los dos CRS no coinciden, y esa es la parte "
                "amable. Lo que no avisa es haberlos igualado con la orden equivocada: "
                "reetiquetar deja los números donde estaban y hace coincidir dos capas que "
                "siguen sin estar en el mismo sitio."),
             op("Comprobar la validez topológica de las localidades antes del cruce.", True,
                "Un polígono con una autointersección no lanza una excepción: devuelve áreas y "
                "resultados de contención que parecen medidas. El denominador del coropleto "
                "sale de ahí."),
             op("Construir el índice espacial a mano para que el cruce dé el resultado "
                "correcto.", False,
                f"El índice no cambia el resultado del cruce, solo lo que cuesta llegar a él "
                f"—de {c('ing_pares_bruta')} pares a {c('ing_pares_cajas')} tras el filtro de "
                f"cajas—, y lo construye la biblioteca sola. Un resultado que dependiera del "
                f"índice sería un defecto del índice."),
             op("Comprobar al final que el mapa se ve bien, que es la validación que de verdad "
                "importa.", False,
                "Es la comprobación que no distingue nada: un CRS mal etiquetado, un cruce mal "
                "hecho y un denominador equivocado producen los tres un mapa perfectamente "
                "creíble. Verse bien es lo que hacen todos estos errores.")],
         retroAcierto="Los dos pasos que hay que dar antes son los que, saltados, no dan "
                      "error: dan un número.",
         retroFallo="Se sostienen reproyectar con la orden correcta y validar la topología antes "
                    "del cruce. Las otras dos confían en el índice o en el aspecto final del "
                    "mapa, y ninguna de las dos cosas comprueba nada."),
]

PREGUNTAS = {"a": BLOQUE_A, "b": BLOQUE_B, "c": BLOQUE_C, "d": BLOQUE_D}


# =====================================================================
# EL ORDEN DE LAS OPCIONES SE DECIDE AQUÍ, Y ES UNA CORRECCIÓN.
#
# Las 29 preguntas con opciones se escribieron poniendo la correcta la
# primera —es lo natural: se piensa la respuesta y luego los distractores—
# y ninguna de las cinco familias de guarda del ensamblador podía verlo,
# porque cada pregunta era impecable por separado. Mirándolas juntas, el
# preparcial entero se aprobaba marcando siempre la (a), sin leer una
# palabra. Lo destapó `audita_preparcial1.py` contando las posiciones.
#
# Se baraja, y no se ordena a mano, por lo de siempre: un orden escrito a
# mano hay que mantenerlo, y una pregunta nueva nace otra vez con la
# correcta delante. La semilla sale del propio JSON y de la identidad de
# la pregunta, así que el orden es el mismo en cada reensamblado —el
# documento es reproducible byte a byte— y no cambia al añadir preguntas
# en otro bloque.
#
# Consecuencia que hay que respetar al redactar: NINGUNA retroalimentación
# puede nombrar una posición. «Las correctas son las dos primeras» deja de
# ser cierto en cuanto esto corre, y el motor ya no lo necesita: el
# desglose de las `multiple` nombra cada opción por su texto. Lo vigila
# `POSICIONALES`, más abajo.
# =====================================================================
def baraja(identidad, opciones):
    r = random.Random(f"{meta['semilla']}·{identidad}")
    orden = list(range(len(opciones)))
    r.shuffle(orden)
    return [opciones[i] for i in orden]


for _clave, _preguntas in PREGUNTAS.items():
    for _i, _q in enumerate(_preguntas, 1):
        if "opciones" in _q:
            _q["opciones"] = baraja(
                f"{_clave}{_i}·{_q['doc']}.m{_q['modulo']}", _q["opciones"])


# =====================================================================
# EL CUESTIONARIO: emisión y guardas
# =====================================================================
def js_str(x):
    return json.dumps(x, ensure_ascii=False)


def _titulo_modulo(doc, modulo):
    return next(f["titulo"] for f in ALC.ALCANCE
                if f["doc"] == doc and f["modulo"] == modulo)


def js_pregunta(q):
    """Una pregunta, escrita como el objeto que el motor espera.

    El `repaso` se arma aquí y no se escribe en cada pregunta: sale del
    capítulo y el módulo que la pregunta declara evaluar. Con `modulo` a
    secas —un número— el resumen del cuestionario resolvería
    `courseData.modules[m-1]`, que en este documento son los BLOQUES del
    preparcial: mandaría a repasar el bloque recién hecho.

    Y lleva `orden`, que no es decorativo. El motor ordena la lista de
    repaso con `(a.orden || 0) - (b.orden || 0) || localeCompare(etiqueta)`:
    sin `orden` las tres claves valen 0, gana el desempate alfabético y la
    lista sale «módulo 1, módulo 10, módulo 11, módulo 2, módulo 3…».
    Se vio en el navegador, fallando el bloque A entero (P3.3); ninguna de
    las 112 comprobaciones del auditor lo miraba, porque el orden lo decide
    el motor en tiempo de ejecución y no el JSON. Capítulo por cien más
    módulo ordena también el bloque D, que cruza los tres capítulos.
    """
    etiqueta = (f"Cap. {q['doc'][3]} · módulo {q['modulo']} — "
                f"{_titulo_modulo(q['doc'], q['modulo'])}")
    campos = [
        f"        tipo: {js_str(q['tipo'])}",
        f"        repaso: {{ orden: {int(q['doc'][3]) * 100 + q['modulo']}, "
        f"etiqueta: {js_str(etiqueta)}, "
        f"href: {js_str(ALC.DOCS[q['doc']])} }}",
        f"        pregunta: {js_str(q['pregunta'])}",
        f"        pista: {js_str(q['pista'])}",
    ]
    if q["tipo"] == "grafico":
        campos.append(f"        alto: {q['alto']}")
        campos.append(f"        descripcionGrafico: {js_str(q['descripcionGrafico'])}")
        campos.append(f"        dibujar: {q['dibujar']}")
    if "respuesta" in q:
        campos.append(f"        respuesta: {q['respuesta']!r}")
        campos.append(f"        tolerancia: {q['tolerancia']!r}")
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


# Las formas de nombrar una posición. Con las opciones barajadas, una
# retroalimentación que diga «las dos primeras» miente, y miente de la peor
# manera: sigue leyéndose bien. Se cazaron catorce escribiendo esto.
# «primera banda de distancia» y «la primera clase» NO son posiciones y por
# eso los patrones nombran la opción, no la palabra suelta.
POSICIONALES = [
    re.compile(r"\blas (dos|tres|cuatro) primeras\b", re.I),
    re.compile(r"\bla (primera|segunda|tercera|cuarta|última) opción\b", re.I),
    re.compile(r"\bla opción [a-d]\)", re.I),
    re.compile(r"\blas primeras\b", re.I),
    re.compile(r"\bla de arriba\b|\bla de abajo\b", re.I),
]


def revisa_preguntas():
    """Lo que no se puede dejar a que alguien lo relea.

    Cinco familias, y las cinco han fallado alguna vez en algún material de
    la casa: una opción sin explicación, dos opciones con la misma
    explicación, una pregunta con cero o dos respuestas correctas, un
    enunciado que regala la respuesta copiándola literalmente, y un bloque
    al que le falta alguno de los cuatro tipos.
    """
    problemas = []
    for bloque, preguntas in PREGUNTAS.items():
        tipos = {q["tipo"] for q in preguntas}
        faltan = {"opcion", "multiple", "numerica", "grafico"} - tipos
        if faltan:
            problemas.append(f"al bloque {bloque.upper()} le faltan tipos: "
                             f"{', '.join(sorted(faltan))}")
        for i, q in enumerate(preguntas, 1):
            ref = f"{bloque.upper()}{i} ({q['doc']}.m{q['modulo']})"
            if not q.get("pista"):
                problemas.append(f"{ref}: sin pista")
            ops = q.get("opciones")
            if q["tipo"] == "numerica":
                if "respuesta" not in q or "tolerancia" not in q:
                    problemas.append(f"{ref}: numérica sin respuesta o sin tolerancia")
                if not q.get("retroFallo"):
                    problemas.append(f"{ref}: numérica sin retroFallo")
                continue
            if not ops:
                problemas.append(f"{ref}: sin opciones")
                continue
            correctas = [o for o in ops if o["correcta"]]
            if q["tipo"] in ("opcion", "grafico") and len(correctas) != 1:
                problemas.append(f"{ref}: {len(correctas)} opciones correctas, "
                                 f"se esperaba 1")
            if q["tipo"] == "multiple" and len(correctas) < 2:
                problemas.append(f"{ref}: una «varias respuestas» con "
                                 f"{len(correctas)} correcta(s)")
            retros = []
            for j, o in enumerate(ops, 1):
                if not o.get("retro", "").strip():
                    problemas.append(f"{ref}, opción {j}: sin retroalimentación")
                retros.append(o.get("retro", ""))
            if len(set(retros)) != len(retros):
                problemas.append(f"{ref}: dos opciones comparten retroalimentación")
            # El enunciado no puede llevar dentro el texto de la correcta. Es
            # la familia que el Taller 1 estrenó, adaptada: aquí la filtración
            # no sería una respuesta escrita en el dato, sino una frase del
            # enunciado que se puede casar con una opción sin entender nada.
            for o in correctas:
                limpio = re.sub(r"<[^>]+>", "", o["texto"]).strip(" .")
                if len(limpio) > 25 and limpio.lower() in q["pregunta"].lower():
                    problemas.append(f"{ref}: el enunciado contiene literalmente "
                                     f"el texto de la opción correcta")
            # Y ninguna retroalimentación puede nombrar una posición: las
            # opciones se barajan, así que la posición no es del autor.
            textos = [q["pregunta"], q.get("pista", ""), q.get("retroAcierto", ""),
                      q.get("retroFallo", "")] + [o.get("retro", "") for o in ops]
            for texto in textos:
                for pat in POSICIONALES:
                    if pat.search(texto):
                        problemas.append(f"{ref}: una retroalimentación nombra una "
                                         f"posición («{pat.search(texto).group(0)}»), "
                                         f"y las opciones van barajadas")
                        break

    # La familia que faltaba, y que ninguna de las cinco de arriba podía ver
    # porque las cinco miran UNA pregunta: dónde cae la respuesta correcta
    # sobre el documento entero. Escritas de una en una, las 29 preguntas con
    # opciones tenían la correcta la primera —el preparcial se aprobaba
    # marcando siempre la (a)—, y cada una era impecable por separado.
    posiciones = {}
    n_una = 0
    for preguntas in PREGUNTAS.values():
        for q in preguntas:
            ops = q.get("opciones")
            if not ops or q["tipo"] == "multiple":
                continue
            n_una += 1
            i = next(j for j, o in enumerate(ops, 1) if o["correcta"])
            posiciones[i] = posiciones.get(i, 0) + 1
    if n_una:
        peor, veces = max(posiciones.items(), key=lambda kv: kv[1])
        reparto = " · ".join(f"{k}: {v}" for k, v in sorted(posiciones.items()))
        if veces > n_una * 0.5:
            problemas.append(
                f"la respuesta correcta cae {veces} de {n_una} veces en la "
                f"posición {peor} ({reparto}): se puede aprobar sin leer")
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
        num, "Bloque A · Datos espaciales y la primera ley", "Block A",
        "Los once módulos del capítulo 1: qué es aleatorio en cada tipo de dato, "
        "qué se rompe cuando hay dependencia y cuánta información hay de verdad "
        "en n observaciones.") + f"""
      <p>Once preguntas, una por módulo del capítulo 1. No siguen el orden de dificultad sino el del
        capítulo, así que si una te para en seco ya sabes a qué módulo volver — y el resumen del
        final te lo dirá con el enlace puesto.</p>

      <p>La mitad de las preguntas de este bloque no van sobre qué es una cifra sino sobre
        <strong>qué no se puede concluir de ella</strong>. Es deliberado: es lo que distingue haber
        leído el capítulo de haberlo entendido, y es lo que el parcial pregunta.</p>

{bloque_quiz("bloque-a", "Bloque A · capítulo 1",
             "Once preguntas de los cuatro tipos. Cada opción lleva su explicación, "
             "también las incorrectas: leerlas cuando aciertas también sirve.")}
      <p>El bloque siguiente hace lo mismo con el capítulo 2, que es donde vive el error número uno
        del curso: confundir reetiquetar con reproyectar.</p>
{CIERRE}"""


def mod_bloque_b(num):
    return cabecera(
        num, "Bloque B · CRS y georreferenciación", "Block B",
        "Los once módulos del capítulo 2: qué destruye cada proyección, qué mide "
        "de verdad cada orden de R, y cuáles de sus errores no dan error.") + f"""
      <p>Once preguntas más, una por módulo del capítulo 2. Este capítulo tiene una particularidad
        que conviene tener presente al responder: casi todos sus errores <strong>devuelven un
        número</strong>. No hay excepción que atrape, no hay aviso en consola, y el mapa se sigue
        viendo bien.</p>

      <p>Por eso varias preguntas de abajo no te piden calcular sino decidir <em>qué comprobarías</em>.
        Esa es la competencia que el módulo 5 y el 8 evalúan de verdad.</p>

{bloque_quiz("bloque-b", "Bloque B · capítulo 2",
             "Once preguntas de los cuatro tipos. Las numéricas aceptan coma o punto "
             "decimal, y la tolerancia va dicha en el enunciado.")}
      <p>Con los dos bloques hechos ya tienes medido dónde estás en los dos primeros capítulos. El
        que viene hace lo mismo con el capítulo 3, del que entra la mitad larga: hasta el efecto
        escala del MAUP.</p>
{CIERRE}"""


def mod_bloque_c(num):
    return cabecera(
        num, "Bloque C · Cartografía y MAUP I", "Block C",
        "Los ocho módulos del capítulo 3 que entran: qué decide quien dibuja un "
        "mapa, qué se ve distinto según cómo se clasifique, y qué le pasa a una "
        "cifra cuando se cambia de escala.") + f"""
      <p>Ocho preguntas, una por cada módulo del capítulo 3 que entra en el parcial. El capítulo
        tiene once y aquí se evalúan hasta el octavo; los tres últimos —zonificación, falacia
        ecológica y ética— están nombrados en el módulo 1 y quedan para el segundo corte.</p>

      <p>Este bloque tiene un aire distinto a los dos anteriores, y conviene saberlo antes de
        empezar: casi ninguna pregunta va sobre si un mapa está bien o mal hecho. Van sobre
        <strong>qué decisiones hay detrás de un mapa que nadie declara en el pie</strong> —el
        esquema, el número de clases, la paleta, la unidad de agregación— y sobre qué cambia en el
        mapa cuando esas decisiones cambian.</p>

{bloque_quiz("bloque-c", "Bloque C · capítulo 3",
             "Ocho preguntas de los cuatro tipos. Dos son de lectura de gráfico: "
             "conviene mirar los ejes antes que la forma de la curva.")}
      <p>Con los tres bloques hechos ya tienes cubierto el temario capítulo por capítulo. Lo que
        viene ahora no son preguntas: son las seis rutinas que el parcial puede pedirte que
        escribas o que leas, con la salida que de verdad devuelven.</p>
{CIERRE}"""


# =====================================================================
# MÓDULO · Los seis procedimientos
#
# Cada bloque se EJECUTÓ para escribir su `#>`, y `verifica_bloques.py`
# los vuelve a ejecutar encadenados y contrasta cada cifra anunciada
# contra la salida real. Ninguno lleva la marca `arranque`: aquí no hay
# nada que el lector tenga que rellenar con sus datos.
#
# Los seis son autónomos —cargan sus paquetes y sus datos— porque el
# preparcial se lee por partes y porque, encadenados con los cuatro
# capítulos, heredarían un entorno que aquí no se puede dar por supuesto.
# El de medir distancias guarda y restaura `sf_use_s2()` por eso mismo:
# el estado de s2 es global y el resultado depende de él.
# =====================================================================
def tabs(etiqueta, r_code, py_code):
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


def mod_procedimientos(num):
    return cabecera(
        num, "Seis rutinas que el parcial puede pedir", "Six routines",
        "Escribir, leer o corregir las seis operaciones que aparecen una y otra "
        "vez en los tres capítulos, y saber con qué línea se comprueba cada una.") + f"""
      <p>No hay nada que responder en este módulo. Son seis procedimientos completos, en R y en
        Python, con la salida <strong>que devuelven de verdad</strong>: se ejecutaron para
        escribirlos y hay un guion del repositorio que los vuelve a ejecutar y comprueba que cada
        línea <code>#&gt;</code> siga cuadrando. Si al leerlos algo no te suena, ese es el módulo al
        que volver.</p>

      <p>Los seis comparten una forma, y esa forma es la mitad de lo que hay que llevarse: cada uno
        termina en <strong>una línea que comprueba</strong>. No porque quede elegante, sino porque
        los errores de estos tres capítulos casi nunca lanzan una excepción — devuelven un número
        con la pinta correcta, y la única defensa es haber mirado.</p>

      <h3>1 · De un CSV a un objeto espacial</h3>
      <p>El paso más frecuente del curso, y el que más silenciosamente se puede hacer mal: las dos
        órdenes piden las coordenadas <strong>en el orden X, Y</strong> —longitud primero—, y con
        las columnas cambiadas de sitio ninguna de las dos protesta.</p>

""" + tabs('De un CSV a un objeto espacial',
      '''library(sf)
est &lt;- read.csv("precalculo/salidas/cap2_estaciones.csv")

# El orden de `coords` es X, Y: longitud PRIMERO.
bien &lt;- st_as_sf(est, coords = c("lon", "lat"), crs = 4326)
cat(sprintf("n = %d | tipo = %s | EPSG = %d\\n", nrow(bien),
            as.character(st_geometry_type(bien)[1]), st_crs(bien)$epsg))
#&gt; n = 361 | tipo = POINT | EPSG = 4326

# La comprobacion: la caja envolvente, en las unidades que toca.
cat(sprintf("caja: lon [%.2f, %.2f]  lat [%.2f, %.2f]\\n",
            st_bbox(bien)[["xmin"]], st_bbox(bien)[["xmax"]],
            st_bbox(bien)[["ymin"]], st_bbox(bien)[["ymax"]]))
#&gt; caja: lon [-81.73, -67.49]  lat [-4.19, 13.36]

# Y asi se ve el MISMO dato con las columnas al reves:
mal &lt;- st_as_sf(est, coords = c("lat", "lon"), crs = 4326)
cat(sprintf("caja: lon [%.2f, %.2f]  lat [%.2f, %.2f]\\n",
            st_bbox(mal)[["xmin"]], st_bbox(mal)[["xmax"]],
            st_bbox(mal)[["ymin"]], st_bbox(mal)[["ymax"]]))
#&gt; caja: lon [-4.19, 13.36]  lat [-81.73, -67.49]''',
      '''import pandas as pd, geopandas as gpd
est = pd.read_csv("precalculo/salidas/cap2_estaciones.csv")

# points_from_xy: x primero, y despues. Mismo orden, otro nombre.
bien = gpd.GeoDataFrame(est, crs=4326,
                        geometry=gpd.points_from_xy(est.lon, est.lat))
print(f"n = {len(bien)} | tipo = {bien.geom_type.iloc[0]} | "
      f"EPSG = {bien.crs.to_epsg()}")
#&gt; n = 361 | tipo = Point | EPSG = 4326

# La comprobacion: la caja envolvente, en las unidades que toca.
x0, y0, x1, y1 = bien.total_bounds
print(f"caja: lon [{x0:.2f}, {x1:.2f}]  lat [{y0:.2f}, {y1:.2f}]")
#&gt; caja: lon [-81.73, -67.49]  lat [-4.19, 13.36]

# Y asi se ve el MISMO dato con las columnas al reves:
mal = gpd.GeoDataFrame(est, crs=4326,
                       geometry=gpd.points_from_xy(est.lat, est.lon))
x0, y0, x1, y1 = mal.total_bounds
print(f"caja: lon [{x0:.2f}, {x1:.2f}]  lat [{y0:.2f}, {y1:.2f}]")
#&gt; caja: lon [-4.19, 13.36]  lat [-81.73, -67.49]''') + f"""
      <p>La segunda caja es la respuesta a «¿cómo sé que lo hice bien?». Una longitud que ronda el 4
        y una latitud que ronda el −70 no existen en Colombia, y se ven en dos segundos. Ninguna
        comprobación automática iba a hacerlo por ti: los dos números son válidos por separado.</p>

      <h3>2 · Reetiquetar o reproyectar</h3>
      <p>El error número uno del curso, y el que mejor mide si el capítulo 2 quedó entendido. Las
        dos órdenes se escriben casi igual, las dos devuelven una capa que se dibuja bien, y solo
        una de las dos recalcula las coordenadas.</p>

""" + tabs('Reetiquetar o reproyectar',
      '''library(sf)
loc &lt;- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
cat(sprintf("el archivo viene en EPSG:%d\\n", st_crs(loc)$epsg))
#&gt; el archivo viene en EPSG:9377

mal  &lt;- st_set_crs(loc, 4326)     # cambia la ETIQUETA
bien &lt;- st_transform(loc, 4326)   # RECALCULA las coordenadas

cat(sprintf("vertices que mueve st_set_crs: %d\\n",
            sum(st_coordinates(mal)[, 1] != st_coordinates(loc)[, 1])))
#&gt; vertices que mueve st_set_crs: 0

# La comprobacion: mirar la caja DESPUES, y ver en que unidades quedo.
cat(sprintf("st_set_crs   -&gt; xmin = %.1f\\n", st_bbox(mal)[["xmin"]]))
#&gt; st_set_crs   -&gt; xmin = 4839066.0
cat(sprintf("st_transform -&gt; xmin = %.5f\\n", st_bbox(bien)[["xmin"]]))
#&gt; st_transform -&gt; xmin = -74.44978''',
      '''import geopandas as gpd
loc = gpd.read_file("datos/procesado/bogota_localidades.gpkg")
print(f"el archivo viene en EPSG:{loc.crs.to_epsg()}")
#&gt; el archivo viene en EPSG:9377

mal  = loc.set_crs(4326, allow_override=True)   # la ETIQUETA
bien = loc.to_crs(4326)                         # las COORDENADAS

# get_coordinates() da una fila por VERTICE, como st_coordinates()
xy_mal, xy_loc = mal.get_coordinates(), loc.get_coordinates()
print(f"vertices que mueve set_crs: {int((xy_mal.x != xy_loc.x).sum())}")
#&gt; vertices que mueve set_crs: 0

print(f"set_crs -&gt; xmin = {mal.total_bounds[0]:.1f}")
#&gt; set_crs -&gt; xmin = 4839066.0
print(f"to_crs  -&gt; xmin = {bien.total_bounds[0]:.5f}")
#&gt; to_crs  -&gt; xmin = -74.44978''') + f"""
      <p>Una capa etiquetada como EPSG:4326 cuya <em>longitud</em> mínima está en los millones no
        está en grados: son los metros del sistema original con una etiqueta nueva encima. Ese es
        el síntoma, y aparece en la caja envolvente antes que en ninguna otra parte.</p>

      <h3>3 · Medir sobre la Tierra, y saber sobre qué superficie</h3>
      <p>Medir una distancia entre dos puntos en grados no es una operación: son tres, según sobre
        qué figura se mida. Y la que se obtiene escribiendo la orden más corta no es la que casi
        todo el mundo cree.</p>

""" + tabs('Medir una distancia, y sobre qué superficie',
      '''library(sf)
bog &lt;- st_sfc(st_point(c(-74.0721, 4.7110)), crs = 4326)
med &lt;- st_sfc(st_point(c(-75.5636, 6.2518)), crs = 4326)

previo &lt;- sf_use_s2()   # el estado de s2 es GLOBAL: se deja como estaba
sf_use_s2(TRUE)         # el de serie: s2 mide sobre una ESFERA de 6 371 010 m
cat(sprintf("st_distance tal cual        = %.0f m\\n",
            as.numeric(st_distance(bog, med))))
#&gt; st_distance tal cual        = 237921 m

cat(sprintf("st_geod_distance (elipsoide) = %.0f m\\n",
            as.numeric(lwgeom::st_geod_distance(bog, med))))
#&gt; st_geod_distance (elipsoide) = 237377 m
invisible(sf_use_s2(previo))''',
      '''import pyproj
# 6 371 010 m es el radio que usa s2, y no el radio medio del WGS84
# (6 371 008,8): con ese, la columna del capitulo 2 no cuadra por 2 cm.
esfera    = pyproj.Geod(a=6371010.0, f=0)
elipsoide = pyproj.Geod(ellps="WGS84")
bog, med = (-74.0721, 4.7110), (-75.5636, 6.2518)

print(f"sobre la esfera    = {esfera.inv(*bog, *med)[2]:.0f} m")
#&gt; sobre la esfera    = 237921 m
print(f"sobre el elipsoide = {elipsoide.inv(*bog, *med)[2]:.0f} m")
#&gt; sobre el elipsoide = 237377 m''') + f"""
      <p>Las dos cifras son correctas y miden cosas distintas. La que devuelve
        <code>st_distance()</code> sin más es la esférica, porque <code>sf</code> usa s2 por
        defecto — y esa es exactamente la columna «esfera» de la tabla del módulo 6, no la
        elipsoidal. En Python la elección es explícita: el <code>Geod</code> lleva escrito sobre qué
        figura mide.</p>

      <h3>4 · Medir dependencia espacial</h3>
      <p>El procedimiento tiene tres pasos y ninguno es el índice: definir quién es vecino de quién,
        decidir qué peso tiene cada vecino y solo entonces calcular. Los dos primeros son
        decisiones, y son las que hay que poder defender.</p>

""" + tabs('El Moran I con pesos de contigüidad',
      '''library(sf); library(spdep)
nc &lt;- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)

nb &lt;- poly2nb(nc, queen = TRUE)   # 1) quien toca a quien
w  &lt;- nb2listw(nb, style = "W")   # 2) pesos, cada fila suma 1
cat(sprintf("n = %d | vecinos por condado = %.1f\\n", nrow(nc), mean(card(nb))))
#&gt; n = 100 | vecinos por condado = 4.9

mt &lt;- moran.test(nc$SID74, w)     # 3) y ahora si, el indice
cat(sprintf("I = %.6f | E[I] sin estructura = %.6f\\n",
            mt$estimate[["Moran I statistic"]], mt$estimate[["Expectation"]]))
#&gt; I = 0.147741 | E[I] sin estructura = -0.010101''',
      '''import geopandas as gpd, numpy as np, json, esda
from libpysal.weights import Queen

# La ruta de nc.shp sale de versiones.json; en R la da system.file().
nc = gpd.read_file(json.load(open("precalculo/versiones.json"))["rutas"]["nc_shp"])

# 1) quien toca a quien
w = Queen.from_dataframe(nc, use_index=False, silence_warnings=True)
print(f"n = {len(nc)} | vecinos por condado = "
      f"{np.mean(list(w.cardinalities.values())):.1f}")
#&gt; n = 100 | vecinos por condado = 4.9

# 2) y 3) en una: esda normaliza los pesos por fila y calcula el indice
mi = esda.Moran(nc["SID74"].values, w)
print(f"I = {mi.I:.6f} | E[I] sin estructura = {mi.EI:.6f}")
#&gt; I = 0.147741 | E[I] sin estructura = -0.010101''') + f"""
      <p>El valor esperado bajo independencia <strong>no es cero</strong>: es −1/(n−1), y por eso el
        índice se compara contra él y no contra el origen. Los dos programas coinciden hasta el
        sexto decimal, que es lo que hay que exigirle a un cruce entre R y Python — y el capítulo 3
        trae el caso en el que <em>no</em> coinciden, que es el siguiente.</p>

      <h3>5 · Clasificar para un coropleto</h3>
      <p>Aquí es donde los dos programas se separan, y no por un error de ninguno: por un convenio
        distinto sobre qué lado del intervalo está cerrado. Se ve solo si hay valores que caen justo
        en un corte, y en un conteo de casos los hay siempre.</p>

""" + tabs('Clasificar por cuantiles, y el convenio del intervalo',
      '''library(classInt)
sid &lt;- read.csv("precalculo/salidas/cap3_nc.csv")$sid74

q &lt;- classIntervals(sid, n = 5, style = "quantile")
cat("cortes:", q$brks, "\\n")
#&gt; cortes: 0 1 4 5 10 44
cat("tamanos:", as.vector(table(findCols(q))), "\\n")
#&gt; tamanos: 13 25 13 26 23

# La comprobacion: cuantos condados caen JUSTO en un corte
cortes &lt;- q$brks[-c(1, length(q$brks))]
cat("condados justo en un corte:", sum(sid %in% cortes), "\\n")
#&gt; condados justo en un corte: 39''',
      '''import pandas as pd, numpy as np, mapclassify as mc
sid = pd.read_csv("precalculo/salidas/cap3_nc.csv")["sid74"].to_numpy()

q = mc.Quantiles(sid, k=5)
# mapclassify lista solo los limites SUPERIORES: son los mismos cortes
# que da R, sin el minimo delante. Lo que si cambia son los tamanos.
print("cortes:", [float(b) for b in q.bins])
#&gt; cortes: [1.0, 4.0, 5.0, 10.0, 44.0]
print("tamanos:", np.bincount(q.yb, minlength=5))
#&gt; tamanos: [24 27 11 19 19]

print("condados justo en un corte:", int(np.isin(sid, q.bins[:-1]).sum()))
#&gt; condados justo en un corte: 39''') + f"""
      <p>Mismo dato, mismo esquema, mismo <em>k</em>, y dos particiones distintas: R cierra el
        intervalo por {c('c3m3_convenio_r')} y Python por {c('c3m3_convenio_py')}. Los dos mapas se
        publicarían con el mismo pie —«clasificación por cuantiles, k = 5»— y no serían el mismo
        mapa. La línea que lo delata es la tercera: contar los empates es lo que convierte una
        sorpresa en una explicación.</p>

      <h3>6 · Agregar y volver a medir</h3>
      <p>La última rutina no calcula nada nuevo: calcula lo mismo dos veces, sobre dos niveles de
        agregación. Es el gesto que hace visible el efecto escala, y cabe en cuatro líneas.</p>

""" + tabs('Agregar y volver a medir',
      '''v &lt;- read.csv("precalculo/salidas/cap3_municipios_edu_madre.csv",
              colClasses = c(divipola = "character"))
cat(sprintf("municipio    n = %4d   r = %.7f\\n", nrow(v), cor(v$x, v$p)))
#&gt; municipio    n = 1114   r = 0.3033294

# Agregar con media PONDERADA por el numero de estudiantes, no simple:
# un municipio de 200 estudiantes no pesa lo mismo que uno de 20 000.
v$dpto &lt;- substr(v$divipola, 1, 2)
dep &lt;- do.call(rbind, lapply(split(v, v$dpto), function(s)
  data.frame(x = weighted.mean(s$x, s$n), p = weighted.mean(s$p, s$n))))
cat(sprintf("departamento n = %4d   r = %.7f\\n", nrow(dep), cor(dep$x, dep$p)))
#&gt; departamento n =   33   r = 0.5126097''',
      '''import pandas as pd, numpy as np
v = pd.read_csv("precalculo/salidas/cap3_municipios_edu_madre.csv",
                dtype={"divipola": str})
print(f"municipio    n = {len(v):4d}   r = {v.x.corr(v.p):.7f}")
#&gt; municipio    n = 1114   r = 0.3033294

# Agregar con media PONDERADA por el numero de estudiantes, no simple:
# un municipio de 200 estudiantes no pesa lo mismo que uno de 20 000.
v["dpto"] = v.divipola.str[:2]
pond = lambda s: pd.Series({"x": np.average(s.x, weights=s.n),
                            "p": np.average(s.p, weights=s.n)})
dep = v.groupby("dpto")[["x", "p", "n"]].apply(pond)
print(f"departamento n = {len(dep):4d}   r = {dep.x.corr(dep.p):.7f}")
#&gt; departamento n =   33   r = 0.5126097''') + f"""
      <p>El mismo dato y la misma fórmula, y dos números que no se parecen. Ninguno de los dos está
        mal: cada uno describe sus unidades. Lo que está mal es publicar uno de ellos sin decir
        sobre qué unidades se calculó, porque quien lo lea supondrá las suyas.</p>

      <p>El bloque que viene es el único que no puede salir de un capítulo suelto: cruza los tres.
        Es también el tipo de pregunta que un parcial hace y una autoevaluación de capítulo no.</p>
{CIERRE}"""


def mod_bloque_d(num):
    return cabecera(
        num, "Bloque D · Integración", "Block D",
        "Reconocer un problema cuando la pista está en un capítulo y la respuesta "
        "en otro, que es la forma que toma casi cualquier pregunta interesante.") + f"""
      <p>Seis preguntas más, y ninguna sale de un solo módulo. Cada una empieza en un capítulo y se
        contesta con lo que dice otro: un mapa del capítulo 3 leído con la pregunta del capítulo 1,
        una cifra del capítulo 2 que decide si un mapa del 3 miente, una operación del 3 cuyo
        resultado depende de algo que el 1 explicó.</p>

      <p>Si un bloque de este preparcial se parece al parcial, es este. No porque sea más difícil
        —no lo es—, sino porque un examen de corte pregunta por el curso y no por el capítulo, y
        estudiar capítulo a capítulo prepara mal para eso.</p>

{bloque_quiz("bloque-d", "Bloque D · los tres capítulos a la vez",
             "Seis preguntas de los cuatro tipos. El enlace de repaso del resumen "
             "apunta al módulo por el que conviene empezar, que no siempre es el "
             "del capítulo donde vive la cifra del enunciado.")}
      <p>Con esto queda recorrido el temario entero. El último módulo reúne los diez errores que se
        repiten, cada uno con la cifra que lo mide y el módulo al que volver.</p>
{CIERRE}"""


QUIZ_JS = "".join(
    f"    AUTOEVALUACIONES['bloque-{clave}'] = [\n"
    + ",\n".join(js_pregunta(q) for q in preguntas)
    + "\n    ];\n\n"
    for clave, preguntas in PREGUNTAS.items())


# =====================================================================
# MÓDULO · Qué entra en el parcial, y qué no
# =====================================================================
def mod_alcance(num):
    bloques = []
    for doc in ("cap1", "cap2", "cap3"):
        filas = [f for f in ALC.ALCANCE if f["doc"] == doc]
        renglones = []
        for f in filas:
            etiqueta = "Módulo " + ent(f["modulo"]) + " · " + f["titulo"]
            renglones.append("          <li>"
                             + enlace_modulo(doc, f["modulo"], etiqueta) + "</li>")
        items = "\n".join(renglones)
        if doc == "cap3":
            hasta = ("Entra <strong>hasta el módulo " + ent(filas[-1]["modulo"])
                     + "</strong>, inclusive.")
        else:
            hasta = "Entra completo: los " + ent(len(filas)) + " módulos de contenido."
        bloques.append(f"""      <h3>{NOMBRE_CAP[doc]}</h3>
        <p>{hasta}</p>
        <ol class="lista-literales" type="1">
{items}
        </ol>""")

    fuera = "\n".join(
        f'          <li><strong>Módulo {f["modulo"]} · {f["titulo"]}</strong></li>'
        for f in ALC.FUERA_DE_ALCANCE)

    return cabecera(
        num, "Qué entra en el parcial, y qué no", "What is on the exam",
        "Nada todavía. Este módulo dice qué se evalúa, qué no, y cómo leer "
        "lo que viene después.") + f"""
      <p>El parcial del Corte I es el <strong>{fecha_larga(meta['fecha_parcial'])}</strong>. Este preparcial no
        tiene nota, se puede repetir tantas veces como quieras y no se envía a ninguna parte: existe
        para que llegues al parcial sabiendo <em>qué</em> sabes, que no es lo mismo que haber leído
        los capítulos.</p>

      <p>No se evalúa recordar cifras. Se evalúan tres cosas distintas, y conviene saber que son
        tres porque se fallan por separado: <strong>el procedimiento</strong> —qué orden llevan los
        pasos y qué pasa si se invierten—, <strong>el concepto</strong> —qué significa una cifra y,
        sobre todo, qué <em>no</em> significa— y <strong>la lectura</strong> —qué dice un gráfico o
        un mapa, y qué no se puede concluir de él—.</p>

      <div class="definition">
        <h3>Cómo funciona</h3>
        <p>Cada bloque trae preguntas de cuatro tipos: opción múltiple, varias respuestas,
          respuesta numérica y lectura de gráfico. Al fallar por primera vez sale una
          <strong>pista</strong> y se puede reintentar; al segundo fallo se revela la respuesta.</p>
        <p style="margin-bottom:0;">Y <strong>todas</strong> las opciones llevan explicación, también
          las incorrectas. No dicen «incorrecto»: dicen a qué error concreto lleva ese razonamiento y
          qué cifra sale de él. Leerlas cuando aciertas también sirve, porque acertar por el motivo
          equivocado es lo que el parcial se encarga de descubrir.</p>
      </div>

      <h3>El temario que entra</h3>
      <p>Son <strong>{ent(meta['n_modulos_alcance'])} módulos</strong>. Cada uno tiene al menos una
        pregunta en este preparcial, y ninguna pregunta sale de esta lista.</p>

{"".join(b + chr(10) for b in bloques)}
      <div class="warning">
        <h3>Lo que NO entra</h3>
        <p>Del capítulo 3 quedan fuera los tres últimos módulos de contenido:</p>
        <ol class="lista-literales" type="1">
{fuera}
        </ol>
        <p style="margin-bottom:0;">Son materia del curso y entran en el segundo corte. En este
          parcial, del MAUP se evalúa <strong>el efecto escala</strong> y no el de zonificación.</p>
      </div>

      <p>El último módulo trae los diez errores que se repiten, con la cifra que mide cada uno y el
        módulo al que conviene volver. Puedes empezar por ahí si prefieres saber dónde están las
        minas antes de pisar el campo.</p>
{CIERRE}"""


# =====================================================================
# MÓDULO · Los diez errores que se repiten
# =====================================================================
def mod_errores(num):
    tarjetas = []
    for e in ERRORES:
        titulo_mod = next(f["titulo"] for f in ALC.ALCANCE
                          if f["doc"] == e["doc"] and f["modulo"] == e["modulo"])
        renglones = [f'            <li>{cifra(c)} — {que(c)}</li>' for c in e["claves"]]
        for nv in e.get("nuevas", []):
            renglones.append(f'            <li>{cifra(nv["ruta"], val_nuevo(nv["ruta"]))}'
                             f' — {nv["que"]}</li>')
        medidas = "\n".join(renglones)
        volver = enlace_modulo(e["doc"], e["modulo"],
                               f"{e['doc'][:3]}. {e['doc'][3]} · módulo {e['modulo']} — {titulo_mod}")
        tarjetas.append(f"""      <div class="tip-box">
        <h3>{e['titulo']}</h3>
        <p>{e['dice']}.</p>
        <p style="margin-bottom:0.5rem;"><strong>Lo que lo mide:</strong></p>
          <ul class="lista-literales">
{medidas}
          </ul>
        <p style="margin-bottom:0;"><strong>Adónde volver:</strong> {volver}.</p>
      </div>""")

    filas_repaso = "\n".join(
        f'            <tr><th scope="row">{f["doc"][:3]}. {f["doc"][3]}</th>'
        f'<td>Módulo {f["modulo"]}</td>'
        f'<td>{enlace_modulo(f["doc"], f["modulo"], f["titulo"])}</td></tr>'
        for f in ALC.ALCANCE)

    return cabecera(
        num, "Los diez errores que se repiten", "The ten that keep coming back",
        "Reconocer, en el enunciado de un problema, cuál de los diez está a "
        "punto de cometerse.") + f"""
      <p>Los diez de abajo tienen algo en común y por eso están juntos: <strong>ninguno da error</strong>.
        El código corre, el mapa sale, el intervalo se imprime y el número que aparece es perfectamente
        razonable. Lo único que falla es que no es el número que se creía estar calculando.</p>

      <p>Cada uno viene con la cifra que lo mide —calculada sobre los datos del curso, no estimada— y
        con el módulo al que volver si al leerlo no reconoces de qué se habla.</p>

{"".join(t + chr(10) for t in tarjetas)}
      <h3>La ruta de repaso completa</h3>
      <p>Los {ent(meta['n_modulos_alcance'])} módulos que entran, en orden, por si prefieres repasar
        por temario en vez de por error.</p>
      <div class="tabla-scroll">
        <table>
          <caption>Los módulos que evalúa el parcial del Corte I</caption>
          <thead>
            <tr><th scope="col">Capítulo</th><th scope="col">Módulo</th><th scope="col">Tema</th></tr>
          </thead>
          <tbody>
{filas_repaso}
          </tbody>
        </table>
      </div>
{CIERRE}"""


# =====================================================================
# El orden del documento. Aquí se insertan los bloques de P2.2 a P2.4,
# entre el primero y el último, y todo se renumera solo.
# =====================================================================
CONSTRUCTORES = [
    (mod_alcance,        "Qué entra en el parcial", "8 min"),
    (mod_bloque_a,       "Bloque A · capítulo 1", "25 min"),
    (mod_bloque_b,       "Bloque B · capítulo 2", "25 min"),
    (mod_bloque_c,       "Bloque C · capítulo 3", "20 min"),
    (mod_procedimientos, "Seis rutinas que el parcial puede pedir", "20 min"),
    (mod_bloque_d,       "Bloque D · integración", "15 min"),
    (mod_errores,        "Los diez errores que se repiten", "15 min"),
]

MODULOS = "".join(f(i + 1) for i, (f, _, _) in enumerate(CONSTRUCTORES))
MODULOS_NAV = [(t, d) for _, t, d in CONSTRUCTORES]

_mods = ",\n".join(
    f'        {{ id: {i + 1}, title: "{t}", duration: "{d}" }}'
    for i, (t, d) in enumerate(MODULOS_NAV))

COURSE_DATA = f"""    const courseData = {{
      modules: [
{_mods}
      ]
    }};

    // El preparcial entero, tal como sale de precalculo/genera_preparcial1.R.
    // Cada cifra reutilizada trae de qué archivo y de qué ruta vino, que es lo
    // que permite a audita_preparcial1.py comprobar que el capítulo no se ha
    // movido debajo.
    const DATOS_PRE1 = {json.dumps(D, ensure_ascii=False)};
"""

VACIO_SIMULADORES = """    // Sin simuladores: este documento no enseña contenido nuevo, así que no
    // tiene nada que manipular. El registro se deja vacío a propósito, para
    // que cuenta_sitio.py no cuente los de demostración de la plantilla como
    // si fueran de este documento.

"""


def reemplaza_region(texto, abre, cierra, nuevo, que_, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes.

    Copiada de `ensambla_taller1.py` con sus dos guardas, y las dos hacen
    falta por lo mismo: sustituir de más se llevó 270 líneas del motor con el
    informe en verde, y sustituir de menos dejó vivos dos simuladores de
    demostración con el archivo bien formado y la consola limpia.
    """
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de «{que_}» aparece "
                 f"{texto.count(abre)} veces, no 1")
    i = texto.index(abre)
    j = texto.index(cierra, i) + len(cierra)
    n_lineas = texto[i:j].count("\n")
    if n_lineas > max_lineas:
        sys.exit(f"PARADO: la región de «{que_}» ocupa {n_lineas} líneas y el tope es "
                 f"{max_lineas}.\n        La plantilla ha cambiado.")
    if n_lineas < min_lineas:
        sys.exit(f"PARADO: la región de «{que_}» ocupa solo {n_lineas} líneas y el "
                 f"mínimo es {min_lineas}.")
    print(f"  OK   {que_}  ({n_lineas} líneas sustituidas)")
    return texto[:i] + nuevo + texto[j:]


def sustituye(texto, ancla, nuevo, que_):
    veces = texto.count(ancla)
    if veces != 1:
        sys.exit(f"PARADO: el ancla de «{que_}» aparece {veces} veces, no 1.\n"
                 f"        {ancla[:90]!r}")
    print(f"  OK   {que_}")
    return texto.replace(ancla, nuevo, 1)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_preparcial1.py (P2.3) ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    # Los identificadores de demostración se LEEN de la plantilla, no se
    # enumeran a mano. La primera versión llevaba la lista escrita y se dejó
    # `MAPAS_ESTACIONALES['demo-mapa']` vivo en el documento publicado: ocho
    # registros conocidos, nueve existentes, y la guarda decía verde sobre los
    # ocho que sabía mirar. Una lista escrita solo sabe cazar lo que ya
    # conocía; la plantilla sabe lo que tiene.
    demos = sorted(set(re.findall(r"[A-Z_]+\['(demo[^']*)'\]", doc))
                   | set(re.findall(r'data-[a-z-]+="(demo[^"]*)"', doc)))
    print(f"  componentes de demostración en la plantilla: {len(demos)} "
          f"({', '.join(demos)})\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Preparcial del Corte I — Estadística Espacial</title>", "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "PREPARCIAL DEL CORTE I •\n"
                    "              CAPÍTULOS 1 Y 2 + CAPÍTULO 3 HASTA MAUP I • SIN NOTA • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Preparcial del Corte I •\n"
                    "          UnBosque 2026-II", "pie")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_PRE1", max_lineas=20)

    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los módulos del preparcial", max_lineas=600)

    doc = reemplaza_region(doc, "    MAPAS_ESTACIONALES['demo-mapa'] = function () {",
                           "\n    };\n", "", "el mapa estacional de demostración",
                           max_lineas=40)
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

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida ----------------------------------------------
    # Que el guion escriba no significa que haya escrito bien.
    marcado = "".join(re.findall(r'<template id="module-.*?</template>', doc, re.S))
    mods = doc.count('<template id="module-')
    declarados = len(MODULOS_NAV)

    try:
        donde = DESTINO.relative_to(RAIZ)
    except ValueError:
        donde = DESTINO
    print(f"\n{donde}  {len(doc)/1024:.0f} KB")
    n_preguntas = sum(len(v) for v in PREGUNTAS.values())
    por_tipo = {}
    for v in PREGUNTAS.values():
        for q in v:
            por_tipo[q["tipo"]] = por_tipo.get(q["tipo"], 0) + 1
    cubiertos = {f"{q['doc']}.m{q['modulo']}"
                 for v in PREGUNTAS.values() for q in v}
    print(f"  {mods} módulos ({declarados} declarados en la navegación) · "
          f"{n_preguntas} preguntas · {len(ERRORES)} errores catalogados · "
          f"{marcado.count('<a href=')} enlaces a los capítulos")
    print(f"  tipos: " + " · ".join(f"{k} {v}" for k, v in sorted(por_tipo.items())))
    print(f"  módulos del alcance con pregunta propia: {len(cubiertos)} de "
          f"{len(ALC.ALCANCE)}")

    problemas = []
    if mods != declarados:
        problemas.append(f"{mods} plantillas de módulo y {declarados} declaradas en la "
                         f"navegación: un botón llevaría a un panel en blanco sin un "
                         f"solo error en consola")
    # El catálogo se llama «los DIEZ errores» en tres sitios de la prosa —el
    # título del módulo, su primer párrafo y el cierre del módulo 1—, y esas
    # tres son cifras escritas con letra: no pasan por `cifra()`, así que
    # `sin_aritmetica.py` no las ve y envejecen en silencio (§12.4). Aquí no
    # se interpolan —«Los 10 errores» se lee peor y el título es un nombre—:
    # se ata el nombre al recuento, que es la otra mitad de la regla.
    NOMBRE_RECUENTO = {10: "diez"}
    palabra = NOMBRE_RECUENTO.get(len(ERRORES))
    if palabra is None or marcado.count(f"{palabra} errores") < 2:
        problemas.append(f"el catálogo tiene {len(ERRORES)} errores y la prosa los "
                         f"llama «{palabra or '?'}»: hay tres sitios que lo escriben "
                         f"con letra y no se actualizan solos")

    # Los 30 módulos del temario tienen que estar NOMBRADOS, no contados. Un
    # preparcial que promete cubrir el temario y se deja tres módulos sin
    # mencionar manda a estudiar a ciegas justo donde no hay preguntas.
    sin_nombrar = [f"{f['doc']}.m{f['modulo']}" for f in ALC.ALCANCE
                   if f["titulo"] not in marcado]
    if sin_nombrar:
        problemas.append(f"{len(sin_nombrar)} módulo(s) del alcance sin nombrar en el "
                         f"documento: {', '.join(sin_nombrar)}")
    # Y los tres que quedan fuera, también por su nombre: decir «hasta el
    # módulo 8» sin decir qué son el 9, el 10 y el 11 es medio aviso.
    fuera_sin_nombrar = [f"{f['doc']}.m{f['modulo']}" for f in ALC.FUERA_DE_ALCANCE
                         if f["titulo"] not in marcado]
    if fuera_sin_nombrar:
        problemas.append(f"módulo(s) fuera del alcance sin nombrar: "
                         f"{', '.join(fuera_sin_nombrar)}")
    # Los demostradores de la plantilla no pueden sobrevivir en un documento
    # publicado: cuenta_sitio.py los contaría como material del preparcial.
    restos = sorted(d for d in demos if f"'{d}'" in doc or f'"{d}"' in doc)
    if restos:
        problemas.append(f"quedan {len(restos)} de los {len(demos)} componentes de "
                         f"demostración de la plantilla: {', '.join(restos)}")
    if "<U+" in doc:
        problemas.append("el documento lleva codificación rota (<U+…>)")
    problemas.extend(revisa_preguntas())
    registradas = len(re.findall(r"\n    AUTOEVALUACIONES\['", doc))
    contenedores = len(re.findall(r'data-quiz="', marcado))
    if registradas != contenedores:
        problemas.append(f"{registradas} cuestionario(s) registrado(s) y "
                         f"{contenedores} contenedor(es) en el marcado: el motor "
                         f"avisa por consola de los que sobran, pero un contenedor "
                         f"sin registro se queda vacío y en silencio")
    # Toda cifra que se cita tiene que existir; y toda cifra que se declara
    # para citarse tiene que citarse. Lo segundo no rompe nada al lector y
    # por eso se olvida: deja PRESENTA creciendo con entradas muertas.
    # `USADAS` lo llena `cifra()` al ejecutarse, así que dice qué se citó DE
    # VERDAD. Contarlo a mano recorriendo el catálogo de errores dejaba fuera
    # las 22 preguntas y denunciaba como huérfanas 45 cifras que sí se usan.
    huerfanas = sorted(set(PRESENTA) - USADAS)
    if huerfanas:
        problemas.append(f"PRESENTA declara cifras que no se citan: "
                         f"{', '.join(huerfanas)}")

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
