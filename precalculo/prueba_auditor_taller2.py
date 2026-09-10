#!/usr/bin/env python3
"""
prueba_auditor_taller2.py — arnés de inyección del auditor del Taller 2 (C4)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_2_Cap_4.md, C4.

Sin esto, `audita_taller2.py` es una opinión: 146 comprobaciones en verde no
dicen nada si ninguna es capaz de ponerse en rojo. Aquí se envenena una copia
del JSON de cien maneras y se comprueba que el auditor las caza todas.

Va ANTES del cierre y no después, que es lo que el plan exige, y por lo que
enseñó el Taller 1: el arnés encontró allí tres defectos que estaban en el
INSTRUMENTO y no en los datos —una trampa de alcance que solo miraba el primer
elemento, una comprobación que nunca se ejecutaba porque el auditor moría antes
con código de error (y el arnés lo contaba como acierto), y un sesgo en el
recuento de la propia cobertura—. Ninguno se ve leyendo el código.

LAS TRES REGLAS, heredadas de `prueba_auditor_base.py`:
  1. cada tanda empieza y acaba con un control sin inyectar;
  2. «N de N cazados» no basta: se cuenta cuántas comprobaciones DISTINTAS
     se han visto fallar, agrupadas por TIPO y no por instancia;
  3. una mutación que no cambia el archivo es error del arnés, no defecto
     no detectado.

Uso:  python3 precalculo/prueba_auditor_taller2.py   (desde `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_taller2.py"

from prueba_auditor_base import arnes  # noqa: E402

ARCHIVOS = {
    "datos": ("TALLER2_DATOS", "taller2_datos.json"),
    "mapas": ("TALLER2_MAPAS", "taller2_mapas.json"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]

# Las comprobaciones que este arnés NO PUEDE romper por construcción, y
# no es una laguna: no leen el JSON que él envenena. Se listan para no
# contarlas como deuda ni esconderlas como cubiertas.
INATACABLES = frozenset({
    "sedes en el GeoPackage",
    "localidades en el GeoPackage",
    "el veredicto vuelca en 3 de las 16",
    "y son Antonio Nariño, Rafael Uribe y Barrios Unidos",
    "en 4 de las 16 ninguna celda llega a esperanza 5",
    "patrones en el CSV entregado",
})


def defectos() -> list[tuple[str, str, str, object]]:
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D: list[tuple[str, str, str, object]] = []

    def obj(nombre, archivo, f):
        D.append((nombre, archivo, "obj", f))

    def txt(nombre, archivo, busca, pone):
        D.append((nombre, archivo, "txt", (busca, pone)))

    def una_loc(o):
        return next(iter(o["localidades"]))

    # --- 1. La respuesta se filtra ------------------------------------
    # Cada uno de estos es el modo de fallo que mata este taller: el JSON
    # viaja dentro del HTML, así que un campo añadido «para depurar»
    # resuelve la tarea en el código fuente de la página.
    # `trios[i]` es una LISTA de tres curvas y `patrones[i]` es un dict:
    # meter la nota en el sitio equivocado no cambia el archivo y el
    # arnés lo declara error suyo, que es la tercera regla del §base.
    for palabra, donde in (("familia", "patrones"), ("agregado", "trios"),
                           ("Thomas", "patrones"), ("aleatorio", "trios"),
                           ("regular", "trios"), ("rSSI", "patrones")):
        obj(f"alguien añade «{palabra}» a {donde} para depurar", "datos",
            (lambda p, d: (lambda o: (o[d][0][0] if d == "trios" else o[d][0])
                           .__setitem__("nota", p)))(palabra, donde))
    obj("el sigma de T5 vuelve a llamarse «sembrado»", "datos",
        lambda o: o["t5"][una_loc(o)].__setitem__("sigma_sembrado", 300))
    obj("un campo de respuesta sobrevive a sin_puntos()", "datos",
        lambda o: o["localidades"][una_loc(o)].__setitem__(".chi_pol", 12.3))
    obj("un campo de respuesta se cuela en los mapas", "mapas",
        lambda o: o["patrones"][0].__setitem__(".orden", "agregado"))
    obj("T5 publica lo que aguantan los selectores", "datos",
        lambda o: o["t5"][una_loc(o)].__setitem__("p4", [5.7, 6.7, 3.1, 3.6]))
    obj("aparece una sección de más en la raíz", "datos",
        lambda o: o.__setitem__("soluciones", {"t1": "la caja"}))
    obj("desaparece una sección de la raíz", "datos",
        lambda o: o.pop("envolventes"))
    obj("una localidad publica un campo de más", "datos",
        lambda o: o["localidades"][una_loc(o)].__setitem__("chi2", 239.8))
    obj("una localidad deja de publicar su lambda", "datos",
        lambda o: o["localidades"][una_loc(o)].pop("lambda"))

    # --- 2. Deja de cuadrar con la fuente primaria --------------------
    obj("el n de una localidad se mueve en uno", "datos",
        lambda o: o["localidades"][una_loc(o)].__setitem__(
            "n", o["localidades"][una_loc(o)]["n"] + 1))
    obj("el área de una localidad se falsea", "datos",
        lambda o: o["localidades"]["Suba"].__setitem__("area_km2", 99.0))
    obj("lambda deja de ser n partido por el área", "datos",
        lambda o: o["localidades"]["Kennedy"].__setitem__("lambda", 7.0))
    obj("aparece una localidad que no llega al mínimo de sedes", "datos",
        lambda o: o["localidades"].__setitem__(
            "Sumapaz", {"cod_loca": "20", "localidad": "Sumapaz", "n": 23,
                        "area_km2": 779.47, "lambda": 0.0295}))
    obj("desaparece una localidad usable", "datos",
        lambda o: o["localidades"].pop("Los Martires"))
    obj("se renombra la CLAVE de una localidad", "datos",
        lambda o: o["localidades"].__setitem__(
            "Suba Norte", o["localidades"].pop("Suba")))
    obj("desaparece la sección de variantes entera", "datos",
        lambda o: o.pop("variantes"))
    obj("una localidad se renombra", "datos",
        lambda o: o["localidades"].__setitem__(
            "Suba", dict(o["localidades"]["Suba"], localidad="Suba Norte")))

    # --- 3. Las curvas dejan de ser las del dato entregado ------------
    obj("la G de un patrón propio se desplaza", "datos",
        lambda o: o["patrones"][0].__setitem__(
            "G", [min(1.0, v + 0.20) for v in o["patrones"][0]["G"]]))
    obj("la G de otro patrón se aplana", "datos",
        lambda o: o["patrones"][11].__setitem__(
            "G", [0.5] * len(o["patrones"][11]["G"])))
    obj("dos patrones intercambian su G", "datos",
        lambda o: (o["patrones"][3].__setitem__("G", o["patrones"][17]["G"]),
                   o["patrones"][17].__setitem__("G", o["patrones"][3]["G"])))
    obj("un patrón publica la G de su vecino", "datos",
        lambda o: o["patrones"][20].__setitem__("G", o["patrones"][21]["G"]))

    # --- 4. La posición del trío vuelve a delatar la familia ----------
    # El defecto que ocurrió de verdad el 2026-09-09: `unname()` quita los
    # nombres y no la posición.
    def reordena(o):
        for t in o["trios"]:
            t.sort(key=lambda c: -c["G"][10])      # el agregado, siempre primero
    obj("los tríos vuelven a ir ordenados por familia", "datos", reordena)

    def reordena_medio(o):
        for t in o["trios"]:
            t.sort(key=lambda c: c["G"][10])       # el regular, siempre primero
    obj("los tríos van ordenados al revés, y también delata", "datos", reordena_medio)

    # --- 4b. La F, que es por donde entró M-14 ------------------------
    # Estas tres existen porque el arnés, la primera vez que se corrió
    # con las comprobaciones nuevas, las declaró «tipos que todavía no
    # ataca». Una comprobación que nadie ha visto fallar es
    # indistinguible de una que no puede fallar, y la F ya se coló una
    # vez precisamente así: el auditor recalculaba G y solo G.
    #
    # La primera reproduce M-14 tal cual: la F rota saturaba en el
    # segundo o tercer nodo de 51, y por eso se pasa de la cota de la
    # unión —los discos de radio r no cubren tanta área— por un factor de
    # cuarenta. Es la inyección que el auditor viejo se habría comido.
    obj("la F satura enseguida, que es exactamente M-14", "datos",
        lambda o: o["patrones"][0].__setitem__(
            "F", [0.0] + [min(1.0, 0.40 + 0.06 * i) for i in range(
                len(o["patrones"][0]["F"]) - 1)]))
    obj("una F baja en un nodo y deja de ser monótona", "datos",
        lambda o: o["trios"][5][1].__setitem__(
            "F", (lambda v: v[:20] + [max(0.0, v[20] - 0.30)] + v[21:])(
                list(o["trios"][5][1]["F"]))))
    # Y una que NO viola la cota ni la monotonía: solo se aparta de la
    # curva de verdad. Si esta se cazara sola por la cota, la comprobación
    # de las sondas no estaría demostrando nada por su cuenta.
    obj("una F se aparta de la de verdad sin violar la cota", "datos",
        lambda o: o["patrones"][9].__setitem__(
            "F", [min(1.0, v * 0.80) for v in o["patrones"][9]["F"]]))

    # --- 5. Las envolventes ------------------------------------------
    obj("el recuento de nodos fuera de banda se infla", "datos",
        lambda o: o["envolventes"][0].__setitem__("nodos_fuera", 99))
    obj("el recuento se pone a cero", "datos",
        lambda o: o["envolventes"][4].__setitem__("nodos_fuera", 0))
    obj("una envolvente declara más nodos de los que tiene", "datos",
        lambda o: o["envolventes"][2].__setitem__("nodos", 600))
    obj("la banda se ensancha hasta que nada se sale", "datos",
        lambda o: (o["envolventes"][6].__setitem__(
            "hi", [v * 10 for v in o["envolventes"][6]["hi"]]),
            o["envolventes"][6].__setitem__(
            "lo", [-abs(v) * 10 for v in o["envolventes"][6]["lo"]])))
    obj("la curva observada se sale por todas partes", "datos",
        lambda o: o["envolventes"][8].__setitem__(
            "obs", [v * 3 for v in o["envolventes"][8]["hi"]]))

    # --- 6. El reparto de las 1000 variantes --------------------------
    obj("una clave de variante se sale del orden", "datos",
        lambda o: o["variantes"][500].__setitem__("clave", "999"))
    obj("faltan variantes", "datos",
        lambda o: o.__setitem__("variantes", o["variantes"][:900]))
    obj("una variante apunta a una localidad inexistente", "datos",
        lambda o: o["variantes"][3].__setitem__("localidad", "Fusagasugá"))
    obj("una variante se contrasta consigo misma", "datos",
        lambda o: o["variantes"][7].__setitem__(
            "contraste", o["variantes"][7]["localidad"]))
    obj("un índice de patrón se sale del catálogo", "datos",
        lambda o: o["variantes"][11].__setitem__("propio", 99))
    obj("un índice de trío es cero", "datos",
        lambda o: o["variantes"][13].__setitem__("trio", 0))
    obj("un índice de envolvente se sale", "datos",
        lambda o: o["variantes"][17].__setitem__("envolvente", 40))
    obj("todas las variantes reciben la misma combinación", "datos",
        lambda o: [v.update({"propio": 1, "trio": 1, "envolvente": 1,
                             "localidad": "Suba"}) for v in o["variantes"]])
    obj("una localidad usable se queda sin ninguna variante", "datos",
        lambda o: [v.__setitem__("localidad", "Suba")
                   for v in o["variantes"] if v["localidad"] == "Los Martires"])

    # --- 7. Formato ---------------------------------------------------
    txt("un NaN se cuela en los datos", "datos", '"n":356', '"n":NaN')
    txt("un infinito se cuela en los mapas", "mapas", '"titulo"', '"inf":1e999,"titulo"')
    obj("un flotante con veinte decimales", "datos",
        lambda o: o["localidades"]["Suba"].__setitem__(
            "area_km2", 100.35470123456789012345))
    txt("mojibake UTF-8 en el JSON", "datos", "Antonio", "Antonio<c3><b1>")

    return D


def main() -> int:
    lista = defectos()

    def tipo(n: str) -> str:
        """Colapsa las instancias de un mismo mecanismo en un solo nombre.

        Sin esto el informe cuenta INSTANCIAS: el auditor repite «su G
        cuadra con la del CSV» veinticuatro veces y «nodos fuera de banda
        recontados» doce, así que un «no visto fallar» abultado asustaría
        sin informar de nada.
        """
        n = re.sub(r"\bpatrón propio \d+\b", "patrón propio N", n)
        n = re.sub(r"\benvolvente \d+\b", "envolvente N", n)
        n = re.sub(r"^[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÜÑáéíóúüñ .]*?: ", "LOCALIDAD: ", n)
        n = re.sub(r"\bposición \d\b", "posición N", n)
        n = re.sub(r"«[^»]*»", "«X»", n)
        # Y se recorta el DETALLE, que `Auditoria.cierto()` imprime pegado
        # al rótulo. Una comprobación cuyo detalle cambia entre pasar y
        # fallar produce dos nombres distintos, así que el recuento por
        # tipos no la ve nunca fallar aunque el arnés la esté tumbando.
        # Encontrado aquí con «sobra [] · falta []» y con el nombre de la
        # localidad pegado a «coincide con su clave».
        n = re.sub(r"(coincide con su clave).*$", r"\1", n)
        n = re.sub(r"\s+sobra .*$", "", n)
        n = re.sub(r"\s+\{.*$", "", n)
        n = re.sub(r"\s+\[.*$", "", n)
        return n.strip()

    return arnes(
        titulo=f"Arnés del auditor del Taller 2 · {len(lista)} inyecciones",
        py=PY, auditor=AUDITOR, salidas=SALIDAS, archivos=ARCHIVOS,
        lista=lista,
        pista_generadores="precalculo/rscript.sh precalculo/genera_taller2.R",
        agrupa=tipo, inatacables=INATACABLES)


if __name__ == "__main__":
    sys.exit(main())
