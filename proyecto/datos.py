"""datos.py — Todo lo que la guía del proyecto integrador AFIRMA con una cifra.

Fechas, pesos, rúbrica, tope, N mínimo y la regla de `nsim` viven aquí y en
ningún otro sitio. El ensamblador (`precalculo/ensambla_proyecto.py`) los
imprime y el auditor (`precalculo/audita_proyecto.py`) los vuelve a calcular
por su cuenta. Una cifra tecleada en dos sitios se despega en uno.

Las decisiones están en `PLAN_Proyecto_Integrador.md`: F1–F6 vienen cerradas
del plan de Series de Tiempo (las fechas, el peso, el canal, el tope y la
conjunta), DE1–DE12 y PE1–PE4 son de esta guía. Cambiar una es tocar UNA línea
de este archivo, reensamblar y volver a auditar.

La tabla de potencia NO está aquí: la produce `proyecto/potencia.R` en
`proyecto/potencia.json`, y este archivo solo la lee.
"""
from __future__ import annotations

import json
import pathlib
from datetime import date, timedelta

AQUI = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# El calendario del curso
# ---------------------------------------------------------------------------
# La numeración de Series y de Espacial (no la de Diseño): la semana 10 va del
# lunes 5 al sábado 10 de octubre de 2026, y la 16, del 16 al 21 de noviembre
# (P1 del plan de Series, cerrada por Javier el 2026-10-21).
SEMANA_10_EMPIEZA = date(2026, 10, 5)

# Los festivos que caen en las semanas del proyecto. Ningún hito va en uno.
FESTIVOS = (date(2026, 11, 2), date(2026, 11, 16))

# Espacial tiene clase los martes y los jueves (el Taller 2 se sustentó el
# martes 13 de octubre y el Parcial 2 fue el jueves 15).
DIAS_DE_CLASE = ("martes", "jueves")


def lunes_de_la_semana(n: int) -> date:
    return SEMANA_10_EMPIEZA + timedelta(weeks=n - 10)


def semana_del_curso(d: date) -> int:
    return 10 + (d - SEMANA_10_EMPIEZA).days // 7


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def frase_fecha(d: date) -> str:
    """«martes 27 de octubre». El día de la semana SALE de la fecha."""
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def frase_semana(n: int) -> str:
    """«del lunes 16 al sábado 21 de noviembre», para una semana del curso."""
    ini, fin = lunes_de_la_semana(n), lunes_de_la_semana(n) + timedelta(days=5)
    if ini.month == fin.month:
        return f"del {DIAS[0]} {ini.day} al {DIAS[5]} {fin.day} de {MESES[fin.month - 1]}"
    return f"del {frase_fecha(ini)} al {frase_fecha(fin)}"


# ---------------------------------------------------------------------------
# F1 · Los hitos: las MISMAS fechas y la misma hora que el proyecto de Series
# ---------------------------------------------------------------------------
HORA_ENTREGA = "11:00"

HITOS = [
    dict(id="ficha", n=1, nombre="Ficha del tema", fecha=date(2026, 10, 27), semana=13,
         entrega="Una ficha de unas 150 palabras: territorio, unidades, fuentes y pregunta"),
    dict(id="preregistro", n=2, nombre="Preregistro", fecha=date(2026, 11, 3), semana=14,
         entrega="El protocolo de inferencia espacial, congelado antes de calcular un solo Moran"),
    dict(id="avance", n=3, nombre="Avance", fecha=date(2026, 11, 10), semana=15,
         entrega="La unión verificada, el mapa exploratorio y la W construida y descrita"),
    dict(id="informe", n=4, nombre="Informe y código", fecha=date(2026, 11, 15), semana=15,
         entrega="El informe, el código que lo produce y los datos"),
]
HITO = {h["id"]: h for h in HITOS}

# La ficha vuelve con respuesta en la primera clase después de su cierre.
RESPUESTA_FICHA = date(2026, 10, 29)

# DE12 · La exposición: en clase, en la semana 16; el día exacto se acuerda en
# clase. Las dos clases de esa semana, porque el lunes 16 es festivo.
SEMANA_EXPOSICION = 16
CLASES_EXPOSICION = (date(2026, 11, 17), date(2026, 11, 19))
DIA_EXPOSICION = "el día exacto se acuerda en clase"
MINUTOS_EXPOSICION = 10
MINUTOS_PREGUNTAS = 5

# DE1 · Equipos
MAX_INTEGRANTES = 2

# Topes de extensión de cada entrega
PALABRAS_FICHA = 150
PAGINAS_PREREGISTRO = 2
PAGINAS_INFORME = 10

# F3 · El canal: un repositorio PRIVADO de GitHub por equipo, con el docente
# como colaborador, y cada hito es una release con su etiqueta. Cuenta la hora
# en que GitHub publica la release, y la release congela lo entregado.
CANAL_ENTREGA = "como una release del repositorio del proyecto en GitHub"
USUARIO_DOCENTE = "JotaMao1985"
NOMBRE_REPO = "proyecto-ee-apellido1-apellido2"
ETIQUETA = {h["id"]: h["id"] for h in HITOS}

# DE5 · Entrega tardía: el 15 % de la nota ORIGINAL por sesión de retraso; la
# primera cuenta desde el cierre y cada clase que empiece sin la release suma otra.
DESCUENTO_POR_SESION = 15
EJEMPLO_RETRASO = 4.0
SESIONES_EJEMPLO = (0, 1, 2, 3)
TUTORIAS = (("martes y viernes", "11:00", "13:00"), ("jueves", "14:00", "16:00"))
DUDAS_EN = "en clase o en las horas de tutoría"

# ---------------------------------------------------------------------------
# F6 · DE10 · La conjunta: sus reglas viven en el módulo 8 de la guía de Series
# ---------------------------------------------------------------------------
SERIES_GUIA = ("https://jotamao1985.github.io/Series-de-Tiempo_Un_Bosque/"
               "proyecto-pronostico-corte-iii.html")
SERIES_MODULO_CONJUNTA = 8
SERIES_ENLACE_CONJUNTA = f"{SERIES_GUIA}#modulo-{SERIES_MODULO_CONJUNTA}"

# ---------------------------------------------------------------------------
# DE3 · PE3 · Cuántas unidades, y la potencia que dan
# ---------------------------------------------------------------------------
N_MINIMO = 25
# Por debajo de este N, un Moran no significativo se lee con la tabla de potencia.
N_LECTURA_POTENCIA = 64
# Las unidades de referencia que la guía nombra (para que el auditor compruebe
# que el umbral las deja dentro o fuera como dice la prosa).
UNIDADES_EJEMPLO = (("los 32 departamentos y Bogotá", 33), ("las 20 localidades de Bogotá", 20))

POTENCIA = json.loads((AQUI / "potencia.json").read_text(encoding="utf-8"))


def potencia(N: int, rho: float) -> float:
    for f in POTENCIA["filas"]:
        if f["N"] == N and abs(f["rho"] - rho) < 1e-9:
            return f["potencia"]
    raise KeyError((N, rho))


# ---------------------------------------------------------------------------
# DE7 · Las réplicas que pide la corrección de multiplicidad (cap. 7, M10)
# ---------------------------------------------------------------------------
# El p bilateral por rangos no baja de 2 / (nsim + 1), y Bonferroni exige
# p < alfa / N ESTRICTO: hace falta nsim + 1 > 2N / alfa. Con alfa = 0,05,
# nsim + 1 > 40·N, es decir nsim ≥ 40·N.
ALFA = 0.05
NSIM_CAPITULO = 49999      # las del cap. 7 para LISA, y las que la guía recomienda
NSIM_HABITUAL = 999        # las de GeoDa y esda


def nsim_minimo_bonferroni(N: int, alfa: float = ALFA) -> int:
    """El menor nsim con 2 / (nsim + 1) < alfa / N."""
    nsim = 1
    while not 2 * N / (nsim + 1) < alfa:     # 2/(nsim+1) < alfa/N, sin dividir
        nsim += 1
    return nsim


N_EJEMPLO_NSIM = 33        # los departamentos

# ---------------------------------------------------------------------------
# PE1 · Pesos: proyecto al 50 % y quices en clase al 50 %, sin examen final
# ---------------------------------------------------------------------------
PROYECTO_DEL_CORTE = 50
QUICES_DEL_CORTE = 50
CORTE_III_DEL_CURSO = 40
PROYECTO_DEL_CURSO = PROYECTO_DEL_CORTE * CORTE_III_DEL_CURSO / 100

NIVELES = [("insuficiente", 1.0), ("aceptable", 3.5), ("sólido", 5.0)]
VALOR_NIVEL = dict(NIVELES)

# ---------------------------------------------------------------------------
# PE4 · La rúbrica de la parte espacial
# ---------------------------------------------------------------------------
# Cada criterio: id, nombre, puntos sobre 100, `foco` (qué mide: sin esa frase
# una rúbrica se lee como una lista de castigos), un descriptor por nivel y,
# donde la variable cambia, `conjunta`: lo que se espera en la opción conjunta.
# `individual` marca lo que se califica persona por persona.
RUBRICA = [
    dict(hito="preregistro", titulo="Preregistro", criterios=[
        dict(id="P1", nombre="El territorio y sus datos", puntos=4,
             foco="Mide si se sabe de dónde sale cada dato y si se puede volver a descargar.",
             insuficiente="Falta la fuente de la geometría o de la variable, o su fecha de "
                          "descarga; no se dice cuántas unidades hay, o no llegan al mínimo.",
             aceptable="Fuentes, fechas y número de unidades, pero sin la llave con que se unen "
                       "la geometría y la variable, o sin el CRS en que se va a medir.",
             solido="Fuentes citables con su fecha de descarga, el tipo y el número de unidades, "
                    "la llave de la unión y el CRS proyectado con su código EPSG."),
        dict(id="P2", nombre="El protocolo de inferencia", puntos=7,
             foco="Mide si las decisiones que mueven el p-valor quedan escritas antes de "
                  "calcularlo: la escala, la variable, la W, las réplicas y la corrección.",
             insuficiente="No se fija la W, o se deja para «la que mejor funcione»; no se dice "
                          "cuántas réplicas ni qué corrección de multiplicidad.",
             aceptable="W principal, réplicas y corrección fijadas, pero sin justificar la W, sin W "
                       "alternativas para la sensibilidad, o con un número de réplicas que no "
                       "alcanza para la corrección elegida.",
             solido="La escala y su porqué, la variable con su normalización, la W principal "
                    "justificada y su estilo, al menos dos W alternativas, un número de réplicas "
                    "que alcanza para la corrección elegida y el nivel.",
             conjunta="En la conjunta, la variable espacial es el MASE de cada unidad (pregunta a) "
                      "o la ganancia de MASE al añadir el rezago espacial (pregunta b), y la W "
                      "principal es la misma con la que se construye ese rezago."),
        dict(id="P3", nombre="Las hipótesis y el plan de análisis", puntos=4,
             foco="Mide si se sabe qué se espera encontrar y qué se hará con cada resultado, "
                  "también con el que no salga significativo.",
             insuficiente="No hay hipótesis espacial, o el plan se reduce a «calcular el Moran».",
             aceptable="Hipótesis de autocorrelación con su dirección, pero sin decir qué análisis "
                       "local sigue ni cómo se va a leer un resultado no significativo.",
             solido="Hipótesis global con su dirección y su razón en el territorio, el análisis "
                    "local que sigue, y qué se concluirá si el Moran no es significativo, con la "
                    "potencia que da el número de unidades."),
    ]),
    dict(hito="avance", titulo="Avance", criterios=[
        dict(id="A1", nombre="La unión verificada y el mapa exploratorio", puntos=5,
             foco="Mide si el dato que entra al análisis es el que se descargó, y si el primer "
                  "mapa pinta lo que debe.",
             insuficiente="No se cuentan las unidades antes y después de unir, o el mapa pinta "
                          "conteos brutos.",
             aceptable="La unión contada y el mapa de la tasa, pero sin el método de clasificación "
                       "o sin explicar las unidades que se perdieron.",
             solido="Unidades contadas antes y después de unir, cada pérdida explicada, y el mapa "
                    "de la tasa con su clasificación y su número de clases declarados."),
        dict(id="A2", nombre="La W construida y descrita", puntos=5,
             foco="Mide si la W preregistrada existe y se sabe cómo es antes de usarla.",
             insuficiente="La W no es la preregistrada, o se usa sin describirla.",
             aceptable="La W preregistrada con su resumen, pero sin decir qué pasa con las islas o "
                       "con los componentes desconectados.",
             solido="La W preregistrada con el reparto de vecinos por unidad, las islas y la "
                    "decisión sobre <code>zero.policy</code>, los componentes conexos, el Moran "
                    "global con esa W y las desviaciones del plan, cada una con su consecuencia.",
             conjunta="En la conjunta, la W se describe sobre las unidades del panel, y el Moran "
                      "del avance se calcula sobre la media de cada unidad en el tramo de "
                      "entrenamiento: los MASE todavía no existen, salen del origen móvil."),
    ]),
    dict(hito="informe", titulo="Informe y código", criterios=[
        dict(id="I1", nombre="Pertinencia del método espacial", puntos=5,
             foco="Mide si el análisis responde la pregunta, a la escala elegida y con el tipo "
                  "de dato que se tiene.",
             insuficiente="El análisis no responde la pregunta, o la escala se eligió por "
                          "comodidad sin decirlo.",
             aceptable="Responde la pregunta, pero no se discute qué cambiaría a otra escala.",
             solido="Responde la pregunta, justifica la escala frente al MAUP y dice qué no "
                    "permite concluir el análisis elegido."),
        dict(id="I2", nombre="Corrección técnica en R", puntos=7,
             foco="Mide si el código hace lo que el informe dice que hace.",
             insuficiente="Vecinos o distancias calculados en grados, una unión que pierde "
                          "unidades sin decirlo, o pesos construidos sin manejar las islas.",
             aceptable="CRS, unión y W correctos, con errores menores: una semilla que falta, un "
                       "estilo de W que no es el declarado.",
             solido="CRS proyectado antes de toda distancia, unión por la llave y no por la "
                    "posición de la fila, la W como se preregistró, permutaciones con semilla y "
                    "cada decisión técnica visible en el código."),
        dict(id="I3", nombre="La autocorrelación global", puntos=8,
             foco="Mide si la inferencia del Moran está bien hecha y se lee entera, también "
                  "cuando no sale significativa.",
             insuficiente="Solo el valor de I, o un p analítico sin decir bajo qué supuesto; no hay "
                          "sensibilidad a la W.",
             aceptable="Moran por permutación con réplicas y semilla, y su diagrama, pero las W "
                       "alternativas se muestran sin leerlas, o un resultado no significativo se "
                       "lee como ausencia de estructura.",
             solido="Moran por permutación con réplicas y semilla, el diagrama de Moran leído por "
                    "cuadrantes, el I bajo cada W preregistrada con su conclusión y, si no es "
                    "significativo, la potencia que daba el número de unidades.",
             conjunta="En la conjunta, el Moran se calcula sobre los MASE por unidad (pregunta a) o "
                      "sobre la ganancia de MASE (pregunta b). Un MASE agrupado en el mapa quiere "
                      "decir que el modelo falla donde fallan sus vecinos."),
        dict(id="I4", nombre="El análisis local", puntos=7,
             foco="Mide si el mapa local dice solo lo que la inferencia permite.",
             insuficiente="Un mapa LISA con los p sin corregir presentado como conglomerados, o una "
                          "corrección que no deja pasar ninguna unidad por falta de réplicas, sin "
                          "decirlo.",
             aceptable="LISA con corrección de multiplicidad, pero sin decir qué p se usó (el "
                       "bilateral o el plegado) o sin comparar el mapa con y sin corrección.",
             solido="LISA con el p bilateral, réplicas suficientes para la corrección, el mapa con "
                    "y sin corrección leído, y G<sub>i</sub>*, si se usa, leído como intensidad y "
                    "no como similitud.",
             conjunta="En la conjunta, el LISA se hace sobre la misma variable que el Moran: los "
                      "MASE o la ganancia de MASE por unidad."),
        dict(id="I5", nombre="Calidad cartográfica", puntos=6,
             foco="Mide si cada mapa se puede leer sin abrir el código.",
             insuficiente="Mapas sin leyenda o sin título, conteos brutos en el coroplético, o las "
                          "categorías LISA con los colores cambiados.",
             aceptable="Mapas legibles y con leyenda, pero sin declarar la clasificación o la "
                       "fuente.",
             solido="Cada mapa con título, leyenda, clasificación y fuente; la tasa y no el conteo; "
                    "las categorías LISA con sus colores de siempre (alto-alto en rojo, bajo-bajo "
                    "en azul) y las islas marcadas aparte."),
        dict(id="I6", nombre="Interpretación en el territorio", puntos=5,
             foco="Mide si la conclusión habla del territorio y no solo de estadísticos.",
             insuficiente="Repite valores p, o afirma causas que un análisis de autocorrelación no "
                          "permite.",
             aceptable="Concluye en el lenguaje del territorio, pero sin sus límites.",
             solido="Concluye en el lenguaje del territorio, nombra los conglomerados por su nombre "
                    "y dice sus límites: la escala, la falacia ecológica y la potencia."),
        dict(id="I7", nombre="Fidelidad al preregistro y reproducibilidad", puntos=4,
             foco="Mide si lo que se hizo es lo que se dijo que se haría, y si cualquiera puede "
                  "volver a hacerlo.",
             insuficiente="El informe no se reproduce desde el repositorio —faltan los datos, hay "
                          "rutas absolutas— o el análisis cambia respecto al preregistro sin decirlo.",
             aceptable="El informe se reproduce, pero el README no dice cómo, los datos crudos se "
                       "editaron a mano o lo exploratorio va mezclado con lo confirmatorio.",
             solido="Se clona el repositorio, se sigue el README y el informe sale entero; los "
                    "datos crudos están intactos, cada desviación del preregistro está declarada "
                    "y lo exploratorio va aparte, marcado como tal."),
        dict(id="I8", nombre="Declaración de uso de IA", puntos=3,
             foco="Mide si se sabe qué hizo la IA y qué se comprobó de lo que hizo.",
             insuficiente="No hay declaración, o dice «se usó IA» sin más.",
             aceptable="Dice qué herramienta y para qué, pero no qué se verificó.",
             solido="Dice qué herramienta, para qué, qué produjo y qué se verificó o corrigió, con "
                    "un ejemplo concreto que se pueda comprobar en el repositorio."),
    ]),
    dict(hito="exposicion", titulo="Exposición", criterios=[
        dict(id="E1", nombre="La exposición", puntos=12,
             foco="Mide si en el tiempo justo se entiende qué se preguntó, cómo y qué se "
                  "concluyó.",
             insuficiente="Se pasa del tiempo, o no se entiende qué se preguntó ni qué se concluyó.",
             aceptable="Cuenta el proyecto en el tiempo, pero sin decir qué salió distinto de lo "
                       "preregistrado.",
             solido="Cuenta en el tiempo la pregunta, la W y por qué, lo que salió distinto, el "
                    "resultado sobre el mapa y sus límites."),
        dict(id="E2", nombre="Las preguntas", puntos=18, individual=True,
             foco="Mide si cada persona puede explicar y defender las decisiones de su propio "
                  "proyecto. En la conjunta, cuentan solo las preguntas de Estadística Espacial.",
             insuficiente="No sabe explicar una decisión de su propio proyecto.",
             aceptable="Explica lo que hizo, pero no por qué ni qué habría pasado de otra manera.",
             solido="Explica lo que hizo, por qué, y qué habría cambiado con otra decisión."),
    ]),
]

HITOS_ESCRITOS = ("preregistro", "avance", "informe")
CRITERIOS = {c["id"]: c for b in RUBRICA for c in b["criterios"]}

# ---------------------------------------------------------------------------
# Lo que el material ya enseñó y la rúbrica pide (frente G del auditor)
# ---------------------------------------------------------------------------
# (capítulo, archivo, módulo, título del módulo, lo que exige, criterios)
EXIGENCIAS = [
    (2, "capitulo-2-crs-georreferenciacion.html", 6, "Medir sobre la Tierra",
     "Un CRS proyectado, y declarado, antes de medir una distancia o buscar vecinos", ("P1", "I2")),
    (3, "capitulo-3-cartografia-maup.html", 2, "Normalizar o mentir",
     "La tasa y no el conteo en el coroplético", ("A1", "I5")),
    (3, "capitulo-3-cartografia-maup.html", 3, "Esquemas de clasificación",
     "La clasificación del mapa, declarada", ("A1", "I5")),
    (3, "capitulo-3-cartografia-maup.html", 8, "MAUP I · el efecto escala",
     "La escala de las unidades como decisión, con su porqué", ("P2", "I1")),
    (3, "capitulo-3-cartografia-maup.html", 10, "La falacia ecológica",
     "No concluir sobre personas lo que se midió sobre áreas", ("I6",)),
    (6, "capitulo-6-pesos-espaciales.html", 9, "Islas y `zero.policy`",
     "Las islas, contadas y con su decisión declarada", ("A2", "I2")),
    (7, "capitulo-7-autocorrelacion.html", 3, "Inferencia",
     "El Moran por permutación, con sus réplicas y su semilla", ("I3",)),
    (7, "capitulo-7-autocorrelacion.html", 7, "Moran es sensible a W",
     "La W fijada antes y la sensibilidad a otras W", ("P2", "I3")),
    (7, "capitulo-7-autocorrelacion.html", 10, "La trampa de la multiplicidad",
     "El mapa LISA con corrección de multiplicidad y réplicas que la permitan", ("P2", "I4")),
    (7, "capitulo-7-autocorrelacion.html", 11, "Getis-Ord G<sub>i</sub> y G<sub>i</sub>*",
     "G<sub>i</sub>* leído como intensidad, no como similitud", ("I4",)),
]

# ---------------------------------------------------------------------------
# F4 · El tope: las preguntas acotan lo escrito
# ---------------------------------------------------------------------------
UMBRAL_TOPE = 3.0


def puntos_de(hito: str) -> int:
    return sum(c["puntos"] for b in RUBRICA if b["hito"] == hito for c in b["criterios"])


def factor_tope(preguntas: float) -> float:
    return min(1.0, preguntas / UMBRAL_TOPE)


def nota_proyecto(escrito: float, exposicion: float, preguntas: float,
                  con_tope: bool = True) -> float:
    """Nota del proyecto en la escala de 5, con lo escrito evaluado en bloque.

    `escrito` es la nota media de preregistro, avance e informe; `exposicion`,
    la de E1; `preguntas`, la de E2 de ESA persona. Redondeada a dos decimales
    aquí, para que lo impreso y lo calculado sean el mismo carácter."""
    f = factor_tope(preguntas) if con_tope else 1.0
    p_esc = sum(puntos_de(h) for h in HITOS_ESCRITOS)
    p_e1, p_e2 = CRITERIOS["E1"]["puntos"], CRITERIOS["E2"]["puntos"]
    return round((p_esc * escrito * f + p_e1 * exposicion + p_e2 * preguntas) / 100, 2)


# Las filas de la tabla del tope: (situación, escrito, exposición, preguntas).
# La nota de las preguntas es la MEDIA de los niveles de las que esa persona
# respondió, así que solo vale lo que una media de 1,0 · 3,5 · 5,0 da: con una
# pregunta, 1,0, 3,5 o 5,0; con dos, además 2,25, 3,0 y 4,25. La exposición
# (E1) es un criterio: 1,0, 3,5 o 5,0. Lo escrito es una media de niveles
# ponderada por los puntos de sus trece criterios. El auditor lo comprueba.
EJEMPLOS_TOPE = [
    ("Proyecto impecable que no sabe defender", 5.0, 5.0, 1.0),
    ("Una pregunta aceptable y otra insuficiente: justo por debajo del umbral", 4.25, 3.5, 2.25),
    ("Proyecto flojo, pero lo defiende bien", 3.0, 3.5, 5.0),
]


def filas_tope() -> list[dict]:
    return [dict(situacion=s, escrito=e, exposicion=x, preguntas=q,
                 factor=round(factor_tope(q), 2),
                 sin_tope=nota_proyecto(e, x, q, con_tope=False),
                 con_tope=nota_proyecto(e, x, q))
            for s, e, x, q in EJEMPLOS_TOPE]


def nota_con_retraso(original: float, sesiones: int) -> float:
    """DE5: el 15 % de la nota ORIGINAL por sesión, sin bajar de 0."""
    return round(max(0.0, original * (1 - sesiones * DESCUENTO_POR_SESION / 100)), 2)


def filas_retraso() -> list[dict]:
    return [dict(sesiones=s, descuento=s * DESCUENTO_POR_SESION,
                 nota=nota_con_retraso(EJEMPLO_RETRASO, s)) for s in SESIONES_EJEMPLO]


# ---------------------------------------------------------------------------
# Formato de las cifras (las mismas grafías que los talleres)
# ---------------------------------------------------------------------------
def nota(x: float) -> str:
    """Escala de 5 con coma decimal y SIEMPRE con decimal: «3,0», «4,5», «2,56»."""
    s = f"{x:.2f}"
    if s.endswith("0"):
        s = s[:-1]
    return s.replace(".", ",")


def divisor(x: float) -> str:
    """El mismo número dentro de una fórmula, con punto y sin decimal sobrante."""
    return f"{x:.2f}".rstrip("0").rstrip(".")


def pct(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def miles(n: int) -> str:
    """«49 999», «1 320»: el separador de miles del material es el espacio fino."""
    s = f"{n:,}".replace(",", " ")
    return s


def decimal(x: float, d: int = 2) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def tutorias_en() -> str:
    return " y ".join(f"<strong>{d} de {i} a {f}</strong>" for d, i, f in TUTORIAS)
