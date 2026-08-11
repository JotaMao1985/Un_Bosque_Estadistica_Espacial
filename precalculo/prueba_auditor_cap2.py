#!/usr/bin/env python3
"""
prueba_auditor_cap2.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T2.1d.

POR QUÉ EXISTE. `audita_cap2.py` informó **426 comprobaciones, 0 fallos**
la primera vez que corrió limpio. Ese número no significa nada por sí solo:
un auditor cuyo silencio no se ha interrogado no es un auditor verificado.

La maquinaria vive en `prueba_auditor_base.py` desde T2.1d. Aquí solo se
declara QUÉ romper, que es lo único propio del capítulo.

LAS FAMILIAS DE DEFECTO. Cada una imita un fallo que ya ocurrió de verdad
en este proyecto o que este capítulo puede sufrir:

   1. cifra publicada que deja de cuadrar con la fuente primaria
   2. cifra derivada que deja de cuadrar con las que la generan
   3. relación cualitativa que se rompe (monotonías, órdenes, signos)
   4. BANDERA que deja de coincidir con el hecho que afirma   ← T1.1, regla 4
   5. propiedad TEÓRICA exacta que se viola (k², sec phi, a·b = s)
   6. discrepancia declarada que pierde su explicación         ← A.2
   7. indicatriz de Tissot alterada                            ← T2.1a
   8. cortes, caja o presupuesto del .geomapa                  ← T0.3
   9. tilde convertida en bytes crudos <c3><b3>                ← T0.5
  10. flotante con más decimales de los declarados             ← T0.5
  11. solución de un ejercicio guiado alterada
  12. coherencia entre módulos rota
  13. ancla externa (la fuente descartada del MEN) desactivada

Uso:  python3 precalculo/prueba_auditor_cap2.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prueba_auditor_base import arnes

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_cap2.py"

ARCHIVOS = {
    "datos": ("CAP2_DATOS", "cap2_datos.json"),
    "mapas": ("CAP2_MAPAS", "cap2_mapas.json"),
    "soluciones": ("CAP2_SOLUCIONES", "cap2_soluciones.json"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


def defectos():
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D = []

    def add(nombre, archivo, f):
        D.append((nombre, archivo, "obj", f))

    def addt(nombre, archivo, busca, pone):
        D.append((nombre, archivo, "txt", (busca, pone)))

    # --- 1. Cifra publicada contra la fuente primaria -------------------
    add("el semieje mayor del WGS84 deja de ser 6 378 137", "datos",
        lambda o: o["elipsoide"].__setitem__("a", 6378130.0))
    add("el aplanamiento inverso cambia de decimal", "datos",
        lambda o: o["elipsoide"].__setitem__("aplanamiento_inv", 298.2572241))
    add("un grado de longitud en el ecuador se acorta", "datos",
        lambda o: o["grados"]["lon_m_elipsoide"].__setitem__(0, 111219.4907))
    add("un grado de latitud en el ecuador se alarga", "datos",
        lambda o: o["grados"]["lat_m_elipsoide"].__setitem__(0, 110674.3886))
    add("la distancia Bogotá-Oslo elipsoidal cambia", "datos",
        lambda o: o["elipsoide"]["esfera_vs_elipsoide"].__setitem__(
            "d_elipsoide_m", 9276484.07))
    add("el desplazamiento de datum de Bogotá cambia", "datos",
        lambda o: o["elipsoide"]["datum"]["desplazamiento_m"].__setitem__(0, 391.86))
    add("el área de Colombia sobre el elipsoide cambia", "datos",
        lambda o: o["medir"]["colombia"].__setitem__("area_elipsoide_km2", 1148265.64))
    add("los municipios dejan de ser 1 122", "datos",
        lambda o: o["epsg"].__setitem__("n_municipios", 1121))
    add("las estaciones dejan de ser 361", "datos",
        lambda o: o["csv_sf"].__setitem__("n", 359))
    add("las sedes de Bogotá dejan de ser 2 209", "datos",
        lambda o: o["posicional"].__setitem__("n_sedes", 2207))
    add("la razón mediana de 3857 sobre los municipios cambia", "datos",
        lambda o: o["epsg"]["filas"][2].__setitem__("razon_med", 1.026079))
    add("el peso del GeoJSON nacional en disco cambia", "datos",
        lambda o: o["formatos"]["pais"].__setitem__("geojson_mb", 190.42731))

    # --- 2. Cifra derivada que deja de cuadrar con su origen ------------
    add("el % del exceso de la esfera no sale de sus dos áreas", "datos",
        lambda o: o["medir"]["colombia"].__setitem__("dif_esfera_pct", 0.61237))
    add("el estiramiento de 9377 no sale de su máximo y su mínimo", "datos",
        lambda o: o["epsg"]["filas"][1].__setitem__("estiramiento", 1.04117))
    add("las sedes por posición no salen del conteo", "datos",
        lambda o: o["posicional"].__setitem__("sedes_por_posicion_2dec", 4.7139))
    add("la reducción del índice no sale de sus dos conteos", "datos",
        lambda o: o["ingenieria"]["join"].__setitem__("reduccion", 19.4137))
    add("la media del desplazamiento de datum no es la de sus cinco", "datos",
        lambda o: o["elipsoide"]["datum"].__setitem__("desp_medio_m", 612.4173))
    add("la razón geojson/gpkg no sale de los dos pesos", "datos",
        lambda o: o["formatos"]["pais"].__setitem__("razon", 3.9174))
    add("la tasa máxima del sesgo no es el máximo de su cuadro", "datos",
        lambda o: o["posicional"]["sesgo"].__setitem__("tasa_max_pct", 19.41732))
    add("la correlación del sesgo no es la de sus dos vectores", "datos",
        lambda o: o["posicional"]["sesgo"].__setitem__("corr_pearson", 0.91473))

    # --- 3. Relación cualitativa rota ----------------------------------
    add("el grado de longitud deja de decrecer con la latitud", "datos",
        lambda o: o["grados"]["lon_m_elipsoide"].__setitem__(5, 141319.0))
    add("el grado de latitud deja de crecer (el elipsoide del revés)", "datos",
        lambda o: o["grados"]["lat_m_elipsoide"].__setitem__(9, 100574.0))
    add("más ruido deja de dar más reasignaciones", "datos",
        lambda o: o["posicional"]["ruidos"][2].__setitem__("pct_cambian", 0.4137))
    add("el cuadro del sesgo se desordena", "datos",
        lambda o: o["posicional"]["sesgo"]["tasa_pct"].reverse())
    add("la celda del geohash deja de encoger al alargarlo", "datos",
        lambda o: o["ingenieria"]["geohash"]["niveles"][2].__setitem__(
            "celda_ancho_km", 91.4173))
    add("las discrepancias del geohash dejan de crecer con la finura", "datos",
        lambda o: o["ingenieria"]["geohash"]["frontera"][0].__setitem__(
            "pct_distinto", 94.1732))
    add("el archipiélago deja de ser el peor caso de 3116", "datos",
        lambda o: o["epsg"]["archipielago"].__setitem__("max_3116_pct", 0.0041))
    add("3857 deja de perder frente a 9377 lejos del meridiano", "datos",
        lambda o: o["epsg"]["bandas"]["err_9377_pct"].__setitem__(5, 9.41732))

    # --- 4. Una BANDERA que deja de coincidir con su hecho --------------
    add("Web Mercator se declara conforme", "datos",
        lambda o: o["proyecciones"]["tabla"]["conforme"].__setitem__(1, True))
    add("Robinson se declara equivalente", "datos",
        lambda o: o["proyecciones"]["tabla"]["equivalente"].__setitem__(4, True))
    add("Mercator deja de declararse conforme", "datos",
        lambda o: o["proyecciones"]["tabla"]["conforme"].__setitem__(0, False))
    add("«gana 9377 el peor caso continental» se invierte", "datos",
        lambda o: o["epsg"].__setitem__("gana_9377_peor_caso_continental", False))
    add("«gana 3116 la mediana continental» se invierte", "datos",
        lambda o: o["epsg"].__setitem__("gana_3116_mediana_continental", False))
    add("«gana 3116 el país entero» se invierte", "datos",
        lambda o: o["epsg"].__setitem__("gana_3116_pais_entero", False))
    add("el capítulo declara que sí hay una conforme y equivalente", "datos",
        lambda o: o["proyecciones"].__setitem__("ninguna_conforme_y_equivalente", False))
    add("el round-trip del geohash se declara completo sin serlo", "datos",
        lambda o: o["ingenieria"]["geohash"]["round_trip"].__setitem__("n_dentro", 11000))
    add("el sesgo por estrato se declara monótono", "datos",
        lambda o: o["posicional"]["por_estrato"].__setitem__("monotono_en_estrato", True))
    add("st_as_sf pasa a declarar que sí hubo aviso", "datos",
        lambda o: o["csv_sf"].__setitem__("hubo_aviso", True))
    add("el shapefile se declara truncador simple", "datos",
        lambda o: o["formatos"]["shapefile"].__setitem__("truncado_simple", True))
    add("E1 declara que la isla NO cambia la respuesta", "soluciones",
        lambda o: o["e1"]["solucion"].__setitem__("la_isla_cambia_la_respuesta", False))
    add("E4 declara que el vecino sí cambia", "soluciones",
        lambda o: o["e4"]["solucion"].__setitem__("vecino_intacto", False))
    add("E2 declara que el buffer en grados cuenta de más", "soluciones",
        lambda o: o["e2"]["solucion"].__setitem__("cuenta_de_menos", False))
    add("E3 declara que las cajas de lon y lat SÍ se solapan", "soluciones",
        lambda o: o["e3"]["solucion"].__setitem__("solapan_las_cajas", True))

    # --- 5. Propiedad TEÓRICA exacta violada ---------------------------
    add("la razón mínima de 9377 deja de ser k²", "datos",
        lambda o: o["epsg"]["filas"][1].__setitem__("razon_min", 0.99741))
    add("la razón mínima de 3116 deja de ser 1", "datos",
        lambda o: o["epsg"]["filas"][0].__setitem__("razon_min", 0.99841))
    add("Mercator deja de cumplir s = k²", "datos",
        lambda o: o["proyecciones"]["mercator"]["area"].__setitem__(2, 2.41732))
    add("la secante declarada de 45° no es sec(45°)", "datos",
        lambda o: o["proyecciones"]["mercator"]["sec_phi"].__setitem__(2, 1.31421))
    add("una indicatriz deja de cumplir a·b = s", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][0]["indicatrices"]["s"].__setitem__(
            3, 9.4173))
    add("un semieje menor supera al mayor", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][2]["indicatrices"]["b"].__setitem__(
            5, 41.732))
    add("una deformación angular sale negativa", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][3]["indicatrices"]["omega"].__setitem__(
            7, -0.4173))
    add("una escala de área sale nula", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][4]["indicatrices"]["s"].__setitem__(
            2, 0.0))

    # --- 6. Discrepancia declarada que pierde su explicación -----------
    add("la discrepancia de s2 se queda sin motivo", "datos",
        lambda o: o["discrepancias"][0].__setitem__("motivo", ""))
    add("la discrepancia de Mollweide se queda sin remedio", "datos",
        lambda o: o["discrepancias"][1].__setitem__("como_recuperar", ""))
    add("desaparecen todas las discrepancias declaradas", "datos",
        lambda o: o.__setitem__("discrepancias", []))

    # --- 7 y 8. Los mapas ----------------------------------------------
    add("la caja de un mapa queda del revés", "mapas",
        lambda o: o["degradado"]["caja"].__setitem__(2, -99.0))
    add("la cuantización de un mapa deja de ser 4096", "mapas",
        lambda o: o["sesgo_localidades"].__setitem__("q", 2048))
    add("un mapa cambia de modo a uno inexistente", "mapas",
        lambda o: o["geohash"].__setitem__("modo", "coropleto"))
    add("el mapa del mundo pierde una vista", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"].pop())
    add("una vista pierde sus indicatrices", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][1].__setitem__("indicatrices", None))
    add("una capa de indicatrices pierde puntos", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][0]["indicatrices"]["x"].pop())
    add("el radio base de las indicatrices se anula", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][5]["indicatrices"].__setitem__("rq", 0.0))

    # --- 9 y 10. Formato -----------------------------------------------
    addt("una tilde se convierte en bytes crudos", "datos", "Bogotá", "Bogot<c3><a1>")
    addt("una tilde se convierte en mojibake latin-1", "soluciones", "área", "Ã¡rea")
    # Sobre un campo PEQUEÑO: en `area_elipsoide_km2`, que ronda el
    # millón, un double no puede llevar once decimales y la inyección no
    # cambiaba nada. El auditor ahora declara ese techo con salta().
    add("un flotante se pasa de decimales declarados", "datos",
        lambda o: o["grados"].__setitem__("bogota_vs_oslo", 1.98812345678901234))
    add("se cuela un NaN en las cifras", "datos",
        lambda o: o["grados"].__setitem__("bogota_vs_oslo", float("nan")))

    # --- 11, 12 y 13. Ejercicios, coherencia y ancla externa -----------
    add("E1 deja de elegir 9377 en el continente", "soluciones",
        lambda o: o["e1"]["solucion"].__setitem__("elegido_continente", "EPSG:3116"))
    add("E2 pierde la monotonía del radio", "soluciones",
        lambda o: o["e2"]["solucion"]["radios"][0].__setitem__("n_cambian", 941))
    add("la tabla de confusión de E3 deja de sumar", "soluciones",
        lambda o: o["e3"]["solucion"].__setitem__("vn", 41))
    add("las discrepancias de E4 dejan de crecer con el umbral", "soluciones",
        lambda o: o["e4"]["solucion"]["umbrales"][0].__setitem__("discrepan", 9417))
    add("E5 deja de cumplir su propio requisito", "soluciones",
        lambda o: o["e5"]["solucion"].__setitem__("tasa_en_sigma_max_pct", 4.1732))
    add("E5 pierde la monotonía de la tasa con sigma", "soluciones",
        lambda o: o["e5"]["solucion"]["tasa_pct"].__setitem__(1, 41.732))
    add("los ejercicios pasan a ser cuatro", "soluciones",
        lambda o: o["meta"].__setitem__("n_ejercicios", 4))
    add("las soluciones cambian de semilla", "soluciones",
        lambda o: o["meta"].__setitem__("semilla", 2027))
    add("el capítulo declarado deja de ser el 2", "datos",
        lambda o: o["meta"].__setitem__("capitulo", 3))
    add("el generador dice haber verificado dos anclas", "datos",
        lambda o: o["meta"].__setitem__("anclas_verificadas", 2))
    add("nuestra degradación deja de reproducir la del MEN", "datos",
        lambda o: o["posicional"]["men_descartada"].__setitem__("n_posiciones", 1900))
    add("el sesgo pasa a medirse con una sola realización", "datos",
        lambda o: o["posicional"]["sesgo"].__setitem__("n_replicas", 1))
    add("el error de Monte Carlo se hincha por encima de la tasa", "datos",
        lambda o: o["posicional"]["sesgo"].__setitem__("emc_global_pct", 2.4173))
    add("una estación invertida pasa a caer en Colombia", "datos",
        lambda o: o["csv_sf"].__setitem__("n_en_colombia", 4))
    add("el shapefile pasa a tener .cpg", "datos",
        lambda o: o["formatos"]["shapefile"].__setitem__("tiene_cpg", True))
    add("el shapefile pasa a ser un solo archivo", "datos",
        lambda o: o["formatos"]["shapefile"].__setitem__("n_archivos", 1))
    add("el GeoPackage pasa a perder los nombres", "datos",
        lambda o: o["formatos"]["gpkg"].__setitem__("nombres_intactos", False))
    add("el lazo pasa a tener área antes de repararse", "datos",
        lambda o: o["topologia"]["lazo"].__setitem__("area_antes", 2.0))
    add("una matriz DE-9IM deja de ser la de la OGC", "datos",
        lambda o: o["topologia"]["de9im"]["matriz"].__setitem__(2, "212101211"))
    add("dos relaciones DE-9IM pasan a tener la misma matriz", "datos",
        lambda o: o["topologia"]["de9im"]["matriz"].__setitem__(
            0, o["topologia"]["de9im"]["matriz"][1]))
    add("st_set_crs pasa a mover coordenadas", "datos",
        lambda o: o["etiquetar"].__setitem__("set_crs_max_delta", 0.4173))
    add("reetiquetar 4686 como 4326 pasa a mover medio kilómetro", "datos",
        lambda o: o["etiquetar"]["silencioso"].__setitem__("desplazamiento_m", 491.73))
    add("un vector de indicatrices cambia de longitud", "mapas",
        lambda o: o["proyecciones_mundo"]["vistas"][2]["indicatrices"]["omega"].pop())
    add("el geohash de San Francisco deja de cuadrar", "datos",
        lambda o: o["ingenieria"]["geohash"]["vectores_canonicos"][1].__setitem__(
            "obtenido", "9q8yyk9y"))
    add("las celdas de un nivel de geohash cambian de conteo", "datos",
        lambda o: o["ingenieria"]["geohash"]["niveles"][3].__setitem__("n_celdas", 1417))
    add("los aciertos exactos superan a los candidatos del índice", "datos",
        lambda o: o["ingenieria"]["join"].__setitem__("aciertos_exactos", 41732))

    return D


def main() -> int:
    return arnes("prueba_auditor_cap2.py — el arnés de inyección del capítulo 2",
                 PY, AUDITOR, SALIDAS, ARCHIVOS, defectos(),
                 "genera_cap2.R y genera_soluciones.R 2")


if __name__ == "__main__":
    sys.exit(main())
