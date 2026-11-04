#!/usr/bin/env python3
"""
calendario_portada.py — el calendario de entregas del proyecto, en la portada

Material de Estadística Espacial 2026-II (20929). 2026-11-04.

La portada lleva el calendario del proyecto integrador: las cuatro entregas y
la exposición, con su fecha, su hora, su peso y la etiqueta de su release. Esas
fechas ya viven en `proyecto/datos.py`, que es la fuente de la guía, y la guía
las imprime en tres sitios distintos. Escribirlas a mano una cuarta vez en la
portada sería abrir el hueco que `datos.py` existe para cerrar: «una cifra
tecleada en dos sitios se despega en uno». Así que este guion las ESCRIBE en la
portada, entre dos comentarios, y escribe también un `.ics` con las cuatro
entregas para que cada quien las añada a su calendario.

Lo que NO escribe es el diseño: el CSS del calendario y el guion que marca qué
entrega cerró y cuál es la próxima viven a mano en `index.html`, porque no
llevan una sola fecha. El guion solo lee los `data-limite` que salen de aquí.

    python3 precalculo/calendario_portada.py            # escribe la portada y el .ics
    python3 precalculo/calendario_portada.py --revisar  # rojo si no están al día con datos.py
    python3 precalculo/calendario_portada.py --prueba   # --revisar, y se rompe a sí mismo

`--revisar` no se fía solo de regenerar y comparar: comprueba también, por su
cuenta y sin `datos.py`, que cada día de la semana impreso es el de su fecha y
que el instante que lee el guion de estados es el mismo que la fecha que se ve.
"""
from __future__ import annotations

import html as _html
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "proyecto"))
import datos as D  # noqa: E402

PORTADA = RAIZ / "index.html"
ICS = RAIZ / "Htmls_Espacial" / "proyecto-integrador-calendario.ics"
ICS_ENLACE = "Htmls_Espacial/proyecto-integrador-calendario.ics"
GUIA_ENLACE = "Htmls_Espacial/proyecto-integrador-corte-iii.html"
SITIO = "https://jotamao1985.github.io/Un_Bosque_Estadistica_Espacial/"

# Bogotá no tiene horario de verano: UTC−5 todo el año. Las entregas cierran a
# las 11:00 de aquí, y el .ics las escribe en UTC para que cada calendario las
# convierta a la hora de quien lo abra.
BOGOTA = timezone(timedelta(hours=-5))

ABRE = ("<!-- CALENDARIO-PROYECTO · lo escribe precalculo/calendario_portada.py desde "
        "proyecto/datos.py: no se edita a mano -->")
CIERRA = "<!-- /CALENDARIO-PROYECTO -->"

MESES_CORTOS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

# El DTSTAMP del .ics: cuándo se publicó el calendario. Fijo, para que el
# archivo salga idéntico cada vez que se regenera y `--revisar` pueda comparar.
PUBLICADO = datetime(2026, 11, 4, 0, 0, tzinfo=timezone.utc)


def e(t: str) -> str:
    return _html.escape(t, quote=False)


def cierre(h: dict) -> datetime:
    return datetime.combine(h["fecha"], time.fromisoformat(D.HORA_ENTREGA), BOGOTA)


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def peso(h: dict) -> str:
    return "Sin nota" if h["id"] == "ficha" else f"{D.puntos_de(h['id'])}&nbsp;% del proyecto"


# ---------------------------------------------------------------------------
# 1. El bloque de la portada
# ---------------------------------------------------------------------------
def li_hito(h: dict) -> str:
    c = cierre(h)
    nota = ""
    if h["id"] == "ficha":
        nota = (f'\n            <p class="hito-nota">La respuesta llega el '
                f'{D.frase_fecha(D.RESPUESTA_FICHA)}, en clase.</p>')
    return f"""        <li class="hito" data-hito="{h['id']}" data-limite="{iso(c)}">
          <div class="hito-fecha" aria-hidden="true"><span class="hito-dia">{h['fecha'].day}</span><span
              class="hito-mes">{MESES_CORTOS[h['fecha'].month - 1]}</span></div>
          <div class="hito-cuerpo">
            <p class="hito-semana">Hito {h['n']} · semana {h['semana']}</p>
            <h3 class="hito-nombre">{e(h['nombre'])}</h3>
            <p class="hito-cierre">Cierra el <time datetime="{iso(c)}">{D.frase_fecha(h['fecha'])} a las
                {D.HORA_ENTREGA}</time></p>
            <p class="hito-que">{e(h['entrega'])}.</p>{nota}
            <p class="hito-pie"><span class="hito-peso">{peso(h)}</span><span>release
                <code>{D.ETIQUETA[h['id']]}</code></span></p>
          </div>
        </li>"""


def li_exposicion() -> str:
    a, b = D.CLASES_EXPOSICION
    desde = datetime.combine(a, time(0, 0), BOGOTA)
    hasta = datetime.combine(b + timedelta(days=1), time(0, 0), BOGOTA)
    dia_a, dia_b = D.frase_fecha(a).rsplit(" de ", 1)[0], D.frase_fecha(b)
    mes = MESES_CORTOS[b.month - 1]
    return f"""        <li class="hito" data-hito="exposicion" data-desde="{iso(desde)}" data-limite="{iso(hasta)}">
          <div class="hito-fecha" aria-hidden="true"><span class="hito-dia doble">{a.day} o {b.day}</span><span
              class="hito-mes">{mes}</span></div>
          <div class="hito-cuerpo">
            <p class="hito-semana">Semana {D.SEMANA_EXPOSICION}</p>
            <h3 class="hito-nombre">Exposición</h3>
            <p class="hito-cierre">En clase, el <time datetime="{a.isoformat()}">{dia_a}</time> o el
              <time datetime="{b.isoformat()}">{dia_b}</time></p>
            <p class="hito-que">{D.MINUTOS_EXPOSICION} minutos por equipo y {D.MINUTOS_PREGUNTAS} de
              preguntas. {D.DIA_EXPOSICION[0].upper() + D.DIA_EXPOSICION[1:]}.</p>
            <p class="hito-pie"><span class="hito-peso">{D.puntos_de('exposicion')}&nbsp;% del
                proyecto</span><span>sin release</span></p>
          </div>
        </li>"""


def bloque() -> str:
    semanas = f"Semanas {D.HITOS[0]['semana']}–{D.SEMANA_EXPOSICION}"
    lis = "\n".join([li_hito(h) for h in D.HITOS] + [li_exposicion()])
    return f"""{ABRE}
    <section class="mb-12" id="calendario-proyecto" aria-labelledby="calendario-proyecto-titulo">
      <div class="corte-rotulo">
        <h2 id="calendario-proyecto-titulo">Calendario del proyecto integrador</h2>
        <span class="corte-semanas">{semanas}</span>
        <span class="corte-lema">Cuatro entregas por release en GitHub y una exposición en clase. El proyecto
          vale el {D.PROYECTO_DEL_CORTE}&nbsp;% del Corte III.</span>
      </div>
      <ol class="calendario">
{lis}
      </ol>
      <div class="calendario-reglas">
        <p>Las cuatro entregas cierran a las <strong>{D.HORA_ENTREGA}, hora de Colombia</strong>, y se entregan
          {D.CANAL_ENTREGA}, con la etiqueta que dice su tarjeta: cuenta la hora en que GitHub publica la
          release. Por cada sesión de retraso se descuenta el {D.DESCUENTO_POR_SESION}&nbsp;% de la nota que
          habría tenido la entrega a tiempo; la ficha no tiene nota, y la exposición no se puede atrasar.</p>
        <p>Son las mismas fechas y la misma hora que las del proyecto de Series de Tiempo, así que la opción
          conjunta no mueve ninguna. Si tienes un acuerdo individual por escrito con el docente, valen las
          fechas de tu acuerdo.</p>
        <p class="calendario-enlaces">
          <a class="tarjeta-abrir" href="{GUIA_ENLACE}">Qué lleva cada entrega, en la guía <i
              class="fas fa-arrow-right" aria-hidden="true"></i></a>
          <a class="tarjeta-abrir" href="{ICS_ENLACE}">Añadir las cuatro entregas a tu calendario <i
              class="fas fa-calendar-plus" aria-hidden="true"></i></a>
        </p>
      </div>
    </section>
    {CIERRA}"""


# ---------------------------------------------------------------------------
# 2. El .ics (RFC 5545)
# ---------------------------------------------------------------------------
def _ics_texto(t: str) -> str:
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _plegar(linea: str) -> list[str]:
    """Una línea de contenido no pasa de 75 octetos: se pliega con CRLF + espacio,
    sin partir un carácter de UTF-8 por la mitad."""
    trozos, actual, tope = [], "", 75
    for ch in linea:
        if len((actual + ch).encode("utf-8")) > tope:
            trozos.append(actual)
            actual, tope = " " + ch, 75
        else:
            actual += ch
    return trozos + [actual]


def ics() -> str:
    utc = "%Y%m%dT%H%M%SZ"
    lineas = ["BEGIN:VCALENDAR", "VERSION:2.0",
              "PRODID:-//Universidad El Bosque//Estadistica Espacial 20929//ES",
              "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
              "X-WR-CALNAME:" + _ics_texto("Proyecto integrador · Estadística Espacial"),
              "X-WR-TIMEZONE:America/Bogota"]
    a, b = D.CLASES_EXPOSICION
    for h in D.HITOS:
        c = cierre(h).astimezone(timezone.utc)
        desc = (f"Cierra a las {D.HORA_ENTREGA}, hora de Colombia. Qué se entrega: {h['entrega'][0].lower() + h['entrega'][1:]}. Va "
                f"{D.CANAL_ENTREGA}, con la etiqueta «{D.ETIQUETA[h['id']]}». "
                + ("No tiene nota. " if h["id"] == "ficha" else
                   f"Vale el {D.puntos_de(h['id'])} % del proyecto, y cada sesión de retraso descuenta "
                   f"el {D.DESCUENTO_POR_SESION} % de esa nota. ")
                + (f"La exposición es en clase, el {D.frase_fecha(a)} o el {D.frase_fecha(b)}: "
                   f"{D.DIA_EXPOSICION}. " if h["id"] == "informe" else "")
                + f"La guía: {SITIO}{GUIA_ENLACE}")
        lineas += ["BEGIN:VEVENT",
                   f"UID:proyecto-ee-2026-ii-{h['id']}@jotamao1985.github.io",
                   f"DTSTAMP:{PUBLICADO.strftime(utc)}",
                   # Sin DTEND: un evento con hora y sin fin «no ocupa tiempo»
                   # (RFC 5545, 3.6.1), que es lo que es un cierre.
                   f"DTSTART:{c.strftime(utc)}",
                   "SUMMARY:" + _ics_texto(f"Proyecto Espacial · cierra: {h['nombre']} "
                                           f"(release {D.ETIQUETA[h['id']]})"),
                   "DESCRIPTION:" + _ics_texto(desc),
                   f"URL:{SITIO}{GUIA_ENLACE}",
                   "TRANSP:TRANSPARENT",
                   "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-P1D",
                   "DESCRIPTION:" + _ics_texto(f"Mañana a las {D.HORA_ENTREGA} cierra: {h['nombre']}"),
                   "END:VALARM", "END:VEVENT"]
    lineas.append("END:VCALENDAR")
    return "".join(t + "\r\n" for l in lineas for t in _plegar(l))


# ---------------------------------------------------------------------------
# 3. La revisión
# ---------------------------------------------------------------------------
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def region(texto: str) -> str | None:
    i = texto.find(ABRE)
    if i < 0 or texto.count(ABRE) != 1 or texto.count(CIERRA) != 1:
        return None
    j = texto.find(CIERRA, i)
    return texto[i:j + len(CIERRA)] if j > i else None


def revisa_bloque(b: str) -> list[str]:
    """Por su cuenta, sin datos.py: lo que se ve tiene que poder ser verdad."""
    problemas = []
    visibles = re.findall(r'<time datetime="(\d{4}-\d\d-\d\d)[^"]*">(.*?)</time>', b, re.S)
    if len(visibles) < len(D.HITOS):
        problemas.append(f"el calendario solo tiene {len(visibles)} fechas visibles")
    for iso_d, txt in visibles:
        d = date.fromisoformat(iso_d)
        txt = re.sub(r"\s+", " ", txt)
        m = re.match(r"(\w+) (\d{1,2})(?: de (\w+))?", txt)
        if not m or int(m.group(2)) != d.day or (m.group(3) and m.group(3) != MESES[d.month - 1]):
            problemas.append(f"«{txt}» no es la fecha de su datetime ({iso_d})")
        elif m.group(1) != DIAS[d.weekday()]:
            problemas.append(f"día de la semana: «{txt}» cae en {DIAS[d.weekday()]}")
    # El guion de estados lee `data-limite`; la gente lee el <time>. Si se
    # despegan, la tarjeta dice una fecha y el «faltan N días» cuenta otra.
    for li in re.findall(r'<li class="hito" data-hito="(?!exposicion)[^"]+"[^>]*>.*?</li>', b, re.S):
        lim = re.search(r'data-limite="([^"]+)"', li)
        vis = re.search(r'<time datetime="([^"]+)"', li)
        if not lim or not vis or lim.group(1) != vis.group(1):
            problemas.append(f"limite: el data-limite y el <time> no coinciden "
                             f"({lim and lim.group(1)} frente a {vis and vis.group(1)})")
    return problemas


def revisa(texto: str, texto_ics: str | None) -> list[str]:
    problemas = []
    b = region(texto)
    if b is None:
        return ["no hay región del calendario en la portada (o hay más de una)"]
    if b != bloque():
        problemas.append("el calendario de la portada no coincide con datos.py: regenéralo")
    problemas += revisa_bloque(b)
    if texto_ics is None:
        problemas.append(f"no existe {ICS_ENLACE}")
    else:
        if texto_ics != ics():
            problemas.append("el .ics no coincide con datos.py: regenéralo")
        lineas = texto_ics.split("\r\n")
        if lineas[-1] != "" or any("\n" in l for l in lineas):
            problemas.append("el .ics no termina cada línea en CRLF")
        largas = [l for l in lineas if len(l.encode("utf-8")) > 75]
        if largas:
            problemas.append(f"el .ics tiene {len(largas)} líneas de más de 75 octetos")
        n = texto_ics.count("BEGIN:VEVENT")
        if n != len(D.HITOS) or n != texto_ics.count("END:VEVENT"):
            problemas.append(f"el .ics tiene {n} eventos y las entregas son {len(D.HITOS)}")
    if ICS_ENLACE not in b or GUIA_ENLACE not in b:
        problemas.append("el calendario no enlaza el .ics o la guía")
    return problemas


def prueba(texto: str, texto_ics: str) -> int:
    print("\n=== Autoprueba: se le inyectan defectos al calendario ===")
    if revisa(texto, texto_ics):
        print("  MAL  el control no está limpio")
        return 1
    print("  OK   control · la portada y el .ics salen limpios")
    av = D.HITO["avance"]
    frase_av = D.frase_fecha(av["fecha"])
    casos = [
        ("una fecha tocada a mano en la portada", "portada",
         f"{av['fecha'].day} de {MESES[av['fecha'].month - 1]}",
         f"{av['fecha'].day + 1} de {MESES[av['fecha'].month - 1]}", "no coincide con datos.py"),
        ("un día de la semana que no es el de su fecha", "portada",
         frase_av, frase_av.replace(DIAS[av["fecha"].weekday()], DIAS[(av["fecha"].weekday() + 1) % 7]),
         "día de la semana"),
        ("el instante del guion despegado de la fecha que se ve", "portada",
         f'data-hito="avance" data-limite="{iso(cierre(av))}"',
         f'data-hito="avance" data-limite="{iso(cierre(av) + timedelta(days=1))}"', "limite"),
        ("la región sin su marca de apertura", "portada", ABRE, "<!-- otra cosa -->", "no hay región"),
        ("el .ics tocado a mano", "ics", "DTSTART:2026111", "DTSTART:2026112", ".ics no coincide"),
    ]
    fallos = 0
    for nombre, donde, viejo, nuevo, clave in casos:
        p, q = texto, texto_ics
        if donde == "portada":
            p = texto.replace(viejo, nuevo, 1)
        else:
            q = texto_ics.replace(viejo, nuevo, 1)
        if (p, q) == (texto, texto_ics):
            print(f"  MAL  INERTE · «{nombre}» no cambió nada")
            fallos += 1
            continue
        probs = revisa(p, q)
        cazado = any(clave in x for x in probs)
        print(f"  {'OK ' if cazado else 'MAL'}  «{nombre}» → " + ("cazado" if cazado else f"pasa ({probs})"))
        fallos += 0 if cazado else 1
    # Y el caso al revés: datos.py cambia y nadie regenera. La portada y el .ics
    # siguen siendo los de antes, y tienen que salir en rojo los dos.
    original = av["fecha"]
    av["fecha"] = original + timedelta(days=1)
    try:
        probs = revisa(texto, texto_ics)
    finally:
        av["fecha"] = original
    cazado = any("portada no coincide" in x for x in probs) and any(".ics no coincide" in x for x in probs)
    print(f"  {'OK ' if cazado else 'MAL'}  «datos.py cambia y no se regenera» → "
          + ("cazado en la portada y en el .ics" if cazado else f"pasa ({probs})"))
    return fallos + (0 if cazado else 1)


def main() -> int:
    args = set(sys.argv[1:])
    texto = PORTADA.read_text(encoding="utf-8")
    texto_ics = ICS.read_bytes().decode("utf-8") if ICS.exists() else None
    if not args:
        b = region(texto)
        if b is None:
            print("PARADO: la portada no tiene la región del calendario (o tiene más de una)")
            return 1
        nuevo = texto.replace(b, bloque())
        if nuevo != texto:
            PORTADA.write_text(nuevo, encoding="utf-8")
        ICS.write_bytes(ics().encode("utf-8"))
        print(f"  OK   {PORTADA.name}: calendario escrito ({len(D.HITOS)} entregas y la exposición)")
        print(f"  OK   {ICS_ENLACE}: {len(D.HITOS)} eventos")
        texto, texto_ics = PORTADA.read_text(encoding="utf-8"), ICS.read_bytes().decode("utf-8")
    problemas = revisa(texto, texto_ics)
    for p in problemas:
        print(f"  MAL  {p}")
    if not problemas:
        print(f"  OK   el calendario de la portada y el .ics están al día con datos.py "
              f"({len(D.HITOS)} entregas, días de la semana y data-limite comprobados)")
    fallos = prueba(texto, texto_ics) if "--prueba" in args and not problemas else 0
    return 1 if problemas or fallos else 0


if __name__ == "__main__":
    sys.exit(main())
