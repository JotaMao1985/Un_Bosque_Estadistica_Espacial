#!/usr/bin/env python3
"""
audita_taller2.py — auditoría independiente del precálculo del Taller 2 (C3)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_2_Cap_4.md.

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R. De estas cifras salen las notas de doce
personas, y el generador vive fuera del repositorio: si este auditor no lo
contrasta, nada lo hace.

QUÉ COMPRUEBA, Y POR QUÉ CADA COSA

  1. QUE NO SE FILTRE LA RESPUESTA. El JSON viaja entero dentro del HTML.
     Tres capas: las palabras prohibidas, los campos exactos de cada
     sección, y la convención del punto —todo campo cuyo nombre empieza
     por punto es una respuesta y `sin_puntos()` debía haberlo quitado—.

  2. QUE LA POSICIÓN DEL TRÍO NO DELATE LA FAMILIA. Esta comprobación
     existe porque el defecto ocurrió: los tríos se publicaban siempre en
     el orden (agregado, aleatorio, regular) y `unname()` quita los
     nombres pero no la posición. La posición 1 tenía la G mayor a corta
     distancia en 12 de 12 tríos. Aquí se clasifica cada patrón por sus
     propias curvas y se comprueba que la familia NO sea predecible por
     la posición. Es lo que el ojo encontró leyendo el JSON, hecho de
     oficio.

  3. LAS DIECISÉIS LOCALIDADES, rehechas desde el GeoPackage con
     geopandas: pertenencia GEOMÉTRICA —no la columna `cod_loca`, que en
     siete sedes de 2 209 dice otra cosa—, n, área y lambda.

  4. EL DEFECTO DEL BOUNDING BOX, recalculado con scipy. Y aquí hay una
     convención que NO se puede esquivar y que ya costó un ancla: R
     `quadrat.test()` es de DOS COLAS por defecto y `1 - chi2.cdf()` es
     la cola superior. Sobre Antonio Nariño el mismo chi² de 12,1443 con
     16 g.l. da p = 0,4536 y p = 0,7340 según cuál se use, y el conjunto
     de localidades que cambia de veredicto NO es el mismo. Este auditor
     implementa las DOS colas, que es lo que corre el estudiante.

  5. LAS CURVAS contra el dato que se entrega. Las coordenadas de los
     patrones no están en el JSON: están en `entrega/datos/
     taller2_patrones.csv`, que es lo que el estudiante descarga. Se
     recalculan G y K desde ese CSV y se contrastan. Cierra el hueco
     donde el material ya se quemó una vez: que las cifras y el dibujo
     sean de patrones distintos no lo ve nadie.

  6. LAS ENVOLVENTES: que el recuento de nodos fuera de banda que se
     publica sea el que dan las curvas publicadas.

  7. EL REPARTO: 1000 filas, claves en base cero sin huecos, las 16
     localidades usadas, y ninguna combinación repetida.

Uso:  <geo_env>/python precalculo/audita_taller2.py   (desde `Estadistica espacial/`)
Devuelve 1 si algo falla.

TALLER2_DATOS y TALLER2_MAPAS permiten apuntar a copias con defectos
inyectados, que es lo que hará `prueba_auditor_taller2.py` en C4. Los
archivos publicados no se tocan nunca.
"""
from __future__ import annotations

import json
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"
ENTREGA = RAIZ / "entrega" / "datos"

from audita_base import Auditoria, carga, decimales, sin_nan  # noqa: E402

# Cada una es la respuesta de una tarea: la familia del patrón (T2) y el
# generador que la produce.
PROHIBIDAS = ("familia", "agregado", "aleatorio", "regular", "thomas",
              "rssi", "rpoispp", "conglomerado", "respuesta", "sembrad")

MIN_SEDES = 35
REJILLA_T1 = 5


def main() -> int:
    import geopandas as gpd
    import numpy as np
    import pandas as pd
    from scipy.spatial import cKDTree
    from scipy.stats import chi2 as chi2d
    from shapely.geometry import box

    a = Auditoria("Precálculo del Taller 2 verificado")
    D, ruta_d = carga("TALLER2_DATOS", "taller2_datos.json", SALIDAS)
    M, ruta_m = carga("TALLER2_MAPAS", "taller2_mapas.json", SALIDAS)
    print(f"\n=== audita_taller2.py · {ruta_d.name} + {ruta_m.name} ===")

    # -----------------------------------------------------------------
    a.titulo("Que no se filtre ninguna respuesta")
    crudo = ruta_d.read_text(encoding="utf-8").lower()
    for palabra in PROHIBIDAS:
        a.cierto(palabra not in crudo, f"el JSON no contiene «{palabra}»")

    def con_punto(o, ruta=""):
        """Todo campo que empieza por punto es una respuesta."""
        malos = []
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and k.startswith("."):
                    malos.append(f"{ruta}/{k}")
                malos += con_punto(v, f"{ruta}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                malos += con_punto(v, f"{ruta}[{i}]")
        return malos

    for nom, obj in (("datos", D), ("mapas", M)):
        malos = con_punto(obj, nom)
        a.cierto(not malos, f"ningún campo de respuesta en «{nom}»", str(malos[:3]))

    RAIZ_ESPERADA = {"meta", "localidades", "t5", "patrones", "trios",
                     "envolventes", "variantes"}
    a.cierto(set(D) == RAIZ_ESPERADA,
             "el JSON publica exactamente las siete secciones previstas",
             str(sorted(set(D) ^ RAIZ_ESPERADA)))

    CAMPOS_LOC = {"cod_loca", "localidad", "n", "area_km2", "lambda"}
    sobra = sorted({c for v in D["localidades"].values() for c in set(v) - CAMPOS_LOC})
    falta = sorted({c for v in D["localidades"].values() for c in CAMPOS_LOC - set(v)})
    a.cierto(not sobra and not falta,
             "de cada localidad se publica SOLO identidad, n, área y lambda",
             f"sobra {sobra} · falta {falta}")

    CAMPOS_T5 = {"localidad", "sigma_informe", "pico_informe", "focos_informe"}
    sobra5 = sorted({c for v in D["t5"].values() for c in set(v) - CAMPOS_T5})
    a.cierto(not sobra5, "de T5 solo viajan el sigma y lo que el informe afirma", str(sobra5))

    # -----------------------------------------------------------------
    a.titulo("Formato")
    a.cierto(not list(sin_nan(D)), "ningún NaN ni infinito en los datos")
    a.cierto(not list(sin_nan(M)), "ningún NaN ni infinito en los mapas")
    muchos = [(r, d) for r, d in decimales(D) if d > 10]
    a.cierto(not muchos, "ningún flotante pasa de diez decimales", str(muchos[:3]))
    a.cierto("<c3>" not in crudo and "<c2>" not in crudo, "sin mojibake UTF-8")

    # -----------------------------------------------------------------
    a.titulo("Las 16 localidades, rehechas con geopandas")
    col = gpd.read_file(PROCESADO / "bogota_colegios.gpkg")
    loc = gpd.read_file(PROCESADO / "bogota_localidades.gpkg")
    a.igual(len(col), 2209, "sedes en el GeoPackage")
    a.igual(len(loc), 20, "localidades en el GeoPackage")

    dentro = {}
    for _, Li in loc.iterrows():
        m = col.geometry.within(Li.geometry) | col.geometry.intersects(Li.geometry)
        dentro[Li.localidad] = col[m]
    n_geo = {k: len(v) for k, v in dentro.items()}
    usables = sorted([k for k, v in n_geo.items() if v >= MIN_SEDES])
    a.cierto(sorted(D["localidades"]) == usables,
             f"las {len(usables)} localidades usables son las que pasan n >= {MIN_SEDES}",
             str(set(D["localidades"]) ^ set(usables)))

    # UN AUDITOR QUE REVIENTA NO INFORMA, y el arnés de C4 cuenta la
    # muerte con código != 0 como «cazado» sin que ninguna comprobación
    # se haya visto fallar. Es la lección del preparcial del 2026-08-26,
    # y aquí la volvieron a destapar seis inyecciones: una localidad
    # renombrada, una sección que desaparece y un campo que falta hacían
    # morir a este auditor con KeyError o IndexError. Ahora informa.
    for nom, pub in D["localidades"].items():
        if not a.cierto(nom in dentro, f"{nom}: existe en el GeoPackage"):
            continue
        # El nombre de la CLAVE y el campo `localidad` de dentro tienen
        # que ser el mismo. Sin esta comprobación, renombrar el campo sin
        # tocar la clave pasaba entero: el enunciado imprimiría un nombre
        # y el mapa otro, con todo lo demás cuadrando.
        a.cierto(pub.get("localidad") == nom,
                 f"{nom}: su campo `localidad` coincide con su clave",
                 str(pub.get("localidad")))
        Li = loc[loc.localidad == nom].iloc[0]
        area = Li.geometry.area / 1e6
        a.igual(len(dentro[nom]), pub.get("n"), f"{nom}: n geométrico")
        a.cerca(area, pub.get("area_km2", float("nan")), f"{nom}: área en km²", rel=1e-6)
        a.cerca(len(dentro[nom]) / area, pub.get("lambda", float("nan")),
                f"{nom}: lambda", rel=1e-6)

    # -----------------------------------------------------------------
    a.titulo("El defecto del bounding box, con la convención de R (DOS colas)")

    def quadrat_dos_colas(pts, poly, k=REJILLA_T1, caja=False):
        x0, y0, x1, y1 = poly.bounds
        bx = np.linspace(x0, x1, k + 1)
        by = np.linspace(y0, y1, k + 1)
        cnt, _, _ = np.histogram2d(pts[:, 0], pts[:, 1], bins=[bx, by])
        c = cnt.ravel()
        if caja:
            esp = np.full(c.size, len(pts) / c.size)
            obs = c
        else:
            ar = np.array([poly.intersection(box(bx[i], by[j], bx[i + 1], by[j + 1])).area
                           for i in range(k) for j in range(k)])
            d = ar > 0
            esp = len(pts) * ar[d] / ar[d].sum()
            obs = c[d]
        chi = float(((obs - esp) ** 2 / esp).sum())
        gl = len(esp) - 1
        # DOS colas, que es el defecto de spatstat::quadrat.test y lo que
        # el estudiante verá. La cola superior sola da otra respuesta y
        # cambia el conjunto de localidades que vuelca.
        sup = chi2d.sf(chi, gl)
        p = 2 * min(sup, 1 - sup)
        return chi, p, esp

    vuelcos = []
    ninguna5 = []
    for nom in D["localidades"]:
        # El mismo `.iloc[0]` sin guardar que ya mató a este auditor una
        # vez, dos secciones más arriba. Lo encontró el arnés de C4 con
        # una inyección de mojibake, que renombra una clave y deja este
        # bucle buscando una localidad que no existe. Guardar UNA
        # aparición y no las dos es exactamente la trampa de alcance que
        # el Taller 1 ya pagó.
        if nom not in dentro:
            continue
        Li = loc[loc.localidad == nom].iloc[0]
        pts = np.c_[dentro[nom].geometry.x.values, dentro[nom].geometry.y.values]
        _, p_pol, esp = quadrat_dos_colas(pts, Li.geometry, caja=False)
        _, p_caja, _ = quadrat_dos_colas(pts, Li.geometry, caja=True)
        if p_caja < 0.05 <= p_pol:
            vuelcos.append(nom)
        if (esp < 5).all():
            ninguna5.append(nom)
    a.cierto(len(vuelcos) == 3,
             "el veredicto vuelca en 3 de las 16", f"{sorted(vuelcos)}")
    a.cierto(set(vuelcos) == {"Antonio Narino", "Rafael Uribe Uribe", "Barrios Unidos"},
             "y son Antonio Nariño, Rafael Uribe y Barrios Unidos", str(sorted(vuelcos)))
    a.cierto(len(ninguna5) == 4,
             "en 4 de las 16 ninguna celda llega a esperanza 5", str(sorted(ninguna5)))

    # -----------------------------------------------------------------
    a.titulo("Las curvas, contra el dato que se ENTREGA")
    csv = ENTREGA / "taller2_patrones.csv"
    if not csv.exists():
        a.salta("las curvas contra el CSV entregado",
                f"no existe {csv.relative_to(RAIZ)}; corre datos_taller2.R")
    else:
        P = pd.read_csv(csv)
        a.igual(P.patron.nunique(), 24 + 12 * 3, "patrones en el CSV entregado")

        def G_empirica(xy, rg):
            t = cKDTree(xy)
            d, _ = t.query(xy, k=2)
            dmin = d[:, 1]
            return np.array([(dmin <= r).mean() for r in rg])

        # G de Kaplan-Meier (lo que publica R) contra la G cruda de aquí:
        # sobre la ventana unidad y con estos n la diferencia es pequeña
        # pero real, así que la tolerancia es holgada y se declara.
        for i in range(min(24, len(D.get("patrones", [])))):
            pub = D["patrones"][i]
            xy = P[P.patron == f"p{i + 1:02d}"][["x", "y"]].to_numpy()
            rg = np.array(pub["r"])
            g = G_empirica(xy, rg)
            dif = float(np.max(np.abs(g - np.array(pub["G"]))))
            a.cierto(dif < 0.08, f"patrón propio {i + 1:02d}: su G cuadra con la del CSV",
                     f"máx dif {dif:.4f}")

        # -------------------------------------------------------------
        # LA F, QUE ES EL AGUJERO POR EL QUE SE COLÓ M-14.
        #
        # Hasta el 2026-09-10 este auditor recalculaba G y solo G, y la
        # sección C de `datos_taller2.R` comparaba G y solo G. Nadie
        # miraba la F, y la F publicada llevaba toda la construcción sin
        # ser la función de espacio vacío: `Fest()` se apoya en
        # `distmap.ppp()`, que en esta instalación devuelve distancias AL
        # CUADRADO. Se apartaba hasta 0,9662 sobre una función que vive
        # en [0, 1] y ni un solo check se puso en rojo.
        #
        # Se comprueban DOS cosas, y la primera es la que importa porque
        # no depende de reimplementar nada:
        #
        #   (1) LA COTA DE LA UNIÓN. Los discos de radio r alrededor de
        #       los n puntos cubren como mucho n·pi·r² de área, así que
        #       la fracción de la ventana erosionada que queda a menos de
        #       r de algún punto no puede pasar de n·pi·r²/|W_-r|. Es
        #       aritmética, no una segunda implementación: una F que la
        #       viole no es una F, venga de donde venga. La rota la
        #       violaba por un factor de 40 en el segundo nodo.
        #   (2) LA CURVA ENTERA, recalculada aquí con la misma rejilla de
        #       sondas de `ppp_F_borde()` pero con `cKDTree` en vez de
        #       `nncross`. Eso sí son dos implementaciones distintas, y
        #       por eso la tolerancia puede ser estrecha.
        # -------------------------------------------------------------
        LADO_SONDAS = 400
        gx = np.linspace(0.0, 1.0, LADO_SONDAS)
        GX, GY = np.meshgrid(gx, gx)
        sondas = np.c_[GX.ravel(), GY.ravel()]
        # distancia al borde del cuadrado unidad
        b_sondas = np.minimum(np.minimum(sondas[:, 0], 1 - sondas[:, 0]),
                              np.minimum(sondas[:, 1], 1 - sondas[:, 1]))

        def F_sondas(xy, rg):
            d, _ = cKDTree(xy).query(sondas, k=1)
            out = np.empty(len(rg))
            for k, r in enumerate(rg):
                usable = b_sondas > r
                out[k] = (d[usable] <= r).mean() if usable.any() else np.nan
            return out

        peor_cota, peor_f, peor_mono = 0.0, 0.0, 0.0
        familias = [("patrones", f"p{i + 1:02d}", D.get("patrones", [])[i])
                    for i in range(len(D.get("patrones", [])))]
        for t, tres in enumerate(D.get("trios", [])):
            for j in range(3):
                familias.append(("trios", f"t{t + 1:02d}{'abc'[j]}", tres[j]))
        for _, ident, pub in familias:
            xy = P[P.patron == ident][["x", "y"]].to_numpy()
            rg = np.array(pub["r"])
            Fp = np.array(pub["F"])
            n = len(xy)
            erosion = np.clip(1 - 2 * rg, 0, None) ** 2
            with np.errstate(divide="ignore", invalid="ignore"):
                cota = np.where(erosion > 0,
                                np.minimum(1.0, n * np.pi * rg ** 2 / np.maximum(erosion, 1e-12)),
                                1.0)
            peor_cota = max(peor_cota, float(np.max(Fp - cota)))
            peor_mono = max(peor_mono, float(np.max(np.maximum(0.0, -np.diff(Fp)))))
            peor_f = max(peor_f, float(np.nanmax(np.abs(Fp - F_sondas(xy, rg)))))
        a.cierto(peor_cota <= 1e-9,
                 "ninguna F se pasa de la cota de la unión",
                 f"peor exceso {peor_cota:.6f}")
        a.cierto(peor_mono <= 1e-9, "las 60 F son monótonas no decrecientes",
                 f"peor bajada {peor_mono:.2e}")
        a.cierto(peor_f < 1e-8,
                 "las 60 F se recalculan sobre 400x400 sondas",
                 f"peor dif {peor_f:.2e}")

    # -----------------------------------------------------------------
    a.titulo("Que la posición del trío no delate la familia")
    # Se clasifica cada patrón por su propia G a corta distancia: los
    # agregados tienen G alta enseguida, los regulares la tienen cero
    # hasta su distancia de inhibición. Después se mira si la posición
    # predice la clase. Es el defecto que ocurrió el 2026-09-09.
    j_corto = 10
    clase_pos = {0: [], 1: [], 2: []}
    for t in D.get("trios", []):
        gs = [t[k]["G"][j_corto] for k in range(3)]
        orden = np.argsort(gs)          # 0 = el más regular, 2 = el más agregado
        for pos, rango in enumerate(np.argsort(orden)):
            clase_pos[pos].append(int(rango))
    n_trios = max(len(D.get("trios", [])), 1)
    for pos in range(3):
        mayoria = max(clase_pos[pos].count(c) for c in (0, 1, 2))
        a.cierto(mayoria <= n_trios * 0.6,
                 f"la posición {pos + 1} no lleva siempre la misma familia",
                 f"{mayoria} de {n_trios}")

    # -----------------------------------------------------------------
    # LO QUE UN ESTUDIANTE PUEDE LEER EN EL REPOSITORIO.
    #
    # El JSON ya se vigila arriba, pero la fuga del §0 no estaba en el
    # JSON: estaba en `datos_taller2.R`, que SÍ se versiona —tiene que
    # hacerlo, es lo que permite reconstruir el dato del enunciado desde
    # fuera— y que hasta el 2026-09-10 regeneraba los sesenta patrones
    # con `set.seed()` y las tres funciones generadoras, metidas en una
    # lista cuyos nombres eran los tres regímenes. Publicaba, sin que
    # nadie lo mirara, cuántas familias hay, cómo se llaman, que cada
    # trío trae una de cada, y —corriéndolo— cuál es cuál.
    #
    # `genera_taller2.R` está en `.gitignore` exactamente por eso. Esta
    # comprobación es la que faltaba: mirar también los guiones que sí
    # viajan. Se ignoran los comentarios, porque el arreglo se explica en
    # ellos y explicar un defecto cerrado no lo reabre.
    a.titulo("Lo que un estudiante puede leer en el repositorio")
    GENERADORES = ["rThomas(", "rpoispp(", "rSSI(", "set.seed("]
    FAMILIAS_EN_CODIGO = ["agregado", "aleatorio", "regular"]
    versionados = [RAIZ / "precalculo" / "datos_taller2.R"]
    for ruta in versionados:
        if not ruta.exists():
            a.salta(f"{ruta.name} · fuga de generación", "el archivo no está")
            continue
        vivas = [ln for ln in ruta.read_text(encoding="utf-8").splitlines()
                 if not ln.lstrip().startswith("#")]
        cuerpo = "\n".join(vivas)
        # La guarda del propio guion parte sus literales para no cazarse
        # a sí misma; aquí se ignoran esas líneas por la misma razón.
        cuerpo = "\n".join(ln for ln in vivas if "paste0(" not in ln)
        malos = [g for g in GENERADORES if g in cuerpo]
        a.cierto(not malos, f"{ruta.name} no sabe generar patrones", str(malos))
        # Los tres regímenes como identificadores del código —no dentro de
        # una cadena de una guarda, que es legítimo— dirían cuántas
        # familias hay y cómo se llaman.
        asignaciones = [ln for ln in vivas
                        if any(f"{f} =" in ln or f"{f} <-" in ln for f in FAMILIAS_EN_CODIGO)]
        a.cierto(not asignaciones,
                 f"{ruta.name} no nombra los regímenes",
                 str(asignaciones[:2]))

    # -----------------------------------------------------------------
    a.titulo("Las envolventes de T4(b)")
    a.cierto("envolventes" in D, "la sección de envolventes existe")
    for i, e in enumerate(D.get("envolventes", [])):
        obs = np.array(e["obs"]); lo = np.array(e["lo"]); hi = np.array(e["hi"])
        fuera = int(((obs > hi) | (obs < lo)).sum())
        a.igual(fuera, e["nodos_fuera"],
                f"envolvente {i + 1:02d}: nodos fuera de banda recontados")
        a.cierto(e["nodos"] == len(obs), f"envolvente {i + 1:02d}: nodos declarados",
                 f"{e['nodos']} vs {len(obs)}")
        a.cierto(fuera >= 1, f"envolvente {i + 1:02d}: se sale en algún nodo", str(fuera))

    # -----------------------------------------------------------------
    a.titulo("El reparto de las 1000 variantes")
    a.cierto("variantes" in D, "la sección de variantes existe")
    V = D.get("variantes", [])
    a.igual(len(V), 1000, "filas de la tabla")
    claves = [v["clave"] for v in V]
    a.cierto(claves == [f"{k:03d}" for k in range(1000)],
             "las claves van de 000 a 999 sin huecos y en orden")
    a.cierto(len({v["localidad"] for v in V}) == len(usables),
             "las 16 localidades se usan")
    firmas = {(v["localidad"], v["propio"], v["trio"], v["envolvente"]) for v in V}
    a.cierto(len(firmas) >= 950,
             "casi ninguna combinación se repite", f"{len(firmas)} distintas de 1000")
    a.cierto(all(v["contraste"] != v["localidad"] for v in V),
             "la localidad de contraste de T4(a) nunca es la propia")
    a.cierto(all(v["localidad"] in D["localidades"] for v in V),
             "toda variante apunta a una localidad publicada")
    a.cierto(all(1 <= v["propio"] <= len(D.get("patrones", [])) for v in V),
             "todo índice de patrón propio existe")
    a.cierto(all(1 <= v["trio"] <= len(D.get("trios", [])) for v in V),
             "todo índice de trío existe")
    a.cierto(all(1 <= v["envolvente"] <= len(D.get("envolventes", [])) for v in V),
             "todo índice de envolvente existe")

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
