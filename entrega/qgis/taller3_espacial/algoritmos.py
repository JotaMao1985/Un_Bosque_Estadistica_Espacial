# -*- coding: utf-8 -*-
"""
algoritmos.py — las cuatro herramientas del Taller 3 en la caja de procesos

Estadística Espacial 2026-II (20929) · Universidad El Bosque

Aquí solo está la fontanería de QGIS: leer capas, comprobar el sistema de
referencia, escribir la tabla y el informe. Las cuentas están en
`nucleo.py`; ábrelo, que para eso está.

LAS TRES COMPROBACIONES QUE HACE TODA HERRAMIENTA, antes de calcular:

  1. las dos capas están en el MISMO sistema de referencia;
  2. ese sistema es proyectado, en metros (capítulo 2: una distancia en
     grados no es una distancia);
  3. la ventana, después del filtro, existe.

Si alguna falla, la herramienta se para y lo dice. No reproyecta por su
cuenta: reproyectar es una decisión, y es tuya.
"""

import hashlib
import os

import numpy as np
from qgis.PyQt.QtCore import QVariant

try:                                    # QGIS 3.38 en adelante, y QGIS 4
    from qgis.PyQt.QtCore import QMetaType
    DOBLE, ENTERO = QMetaType.Type.Double, QMetaType.Type.Int
except (ImportError, AttributeError):   # QGIS 3.34 y 3.36
    DOBLE, ENTERO = QVariant.Double, QVariant.Int
from qgis.core import (
    Qgis,
    QgsExpression,
    QgsFeature,
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterExpression,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsRectangle,
    QgsUnitTypes,
    QgsWkbTypes,
)

from . import nucleo as N

VERSION = "1.0.0"
VERDE, NARANJA, GRIS = "#012820", "#FF6600", "#777777"


# ---------------------------------------------------------------------
# Lo común
# ---------------------------------------------------------------------
def _anillos(geom):
    """Anillos de un polígono o multipolígono de QGIS, como arreglos N x 2."""
    partes = geom.asMultiPolygon() if geom.isMultipart() else [geom.asPolygon()]
    return [np.array([[p.x(), p.y()] for p in anillo], dtype=float)
            for parte in partes for anillo in parte if len(anillo) >= 3]


class _Base(QgsProcessingAlgorithm):
    PUNTOS, VENTANA, FILTRO = "PUNTOS", "VENTANA", "FILTRO"

    def group(self):
        return ""

    def groupId(self):
        return ""

    def createInstance(self):
        return type(self)()

    def _params_patron(self):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.PUNTOS, "Capa de puntos (el patrón)", [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.VENTANA, "Capa de polígonos (la ventana)", [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterExpression(
            self.FILTRO, "Filtro de la ventana, p. ej. \"localidad\" = 'Kennedy' (vacío: todos los polígonos)",
            defaultValue="", parentLayerParameterName=self.VENTANA, optional=True))

    def _patron(self, parameters, context, feedback):
        """Devuelve (x, y, anillos, geometría de la ventana, área, crs)."""
        pts = self.parameterAsSource(parameters, self.PUNTOS, context)
        ven = self.parameterAsSource(parameters, self.VENTANA, context)
        if pts is None or ven is None:
            raise QgsProcessingException("Falta la capa de puntos o la de la ventana.")
        crs = ven.sourceCrs()
        if pts.sourceCrs() != crs:
            raise QgsProcessingException(
                "Los puntos están en %s y la ventana en %s. Reproyecta una de las dos capas "
                "(Vectorial > Herramientas de gestión de datos > Reproyectar capa) y vuelve a correr."
                % (pts.sourceCrs().authid(), crs.authid()))
        if crs.isGeographic() or crs.mapUnits() != QgsUnitTypes.DistanceMeters:
            raise QgsProcessingException(
                "El sistema de referencia %s no mide en metros. Estas herramientas calculan distancias "
                "y áreas en el plano: reproyecta las dos capas a EPSG:9377." % crs.authid())

        filtro = (self.parameterAsExpression(parameters, self.FILTRO, context) or "").strip()
        pedido = QgsFeatureRequest()
        if filtro:
            exp = QgsExpression(filtro)
            if exp.hasParserError():
                raise QgsProcessingException("El filtro no se puede leer: " + exp.parserErrorString())
            pedido.setFilterExpression(filtro)
        geoms = [f.geometry() for f in ven.getFeatures(pedido) if f.hasGeometry()]
        if not geoms:
            raise QgsProcessingException("El filtro no deja ningún polígono: no hay ventana.")
        w = QgsGeometry.unaryUnion(geoms) if len(geoms) > 1 else QgsGeometry(geoms[0])
        anillos = _anillos(w)
        a = N.area(anillos)

        xy = np.array([[f.geometry().asPoint().x(), f.geometry().asPoint().y()]
                       for f in pts.getFeatures() if f.hasGeometry()], dtype=float)
        if not len(xy):
            raise QgsProcessingException("La capa de puntos está vacía.")
        ok = N.dentro(xy[:, 0], xy[:, 1], anillos)
        x, y = xy[ok, 0], xy[ok, 1]
        if len(x) < 2:
            raise QgsProcessingException("Dentro de la ventana hay menos de dos puntos.")
        feedback.pushInfo("Ventana: %d polígono(s), %.5f km², %d vértices, %s"
                          % (len(geoms), a / 1e6, sum(len(r) for r in anillos), crs.authid()))
        feedback.pushInfo("Patrón: %d puntos dentro de la ventana, de %d en la capa" % (len(x), len(xy)))
        feedback.pushInfo("Intensidad: %.5f puntos por km²" % (len(x) / a * 1e6))
        return x, y, anillos, w, a, crs

    @staticmethod
    def _rg(rmax, paso):
        if rmax <= 0 or paso <= 0 or paso > rmax:
            raise QgsProcessingException("El radio máximo y el paso tienen que ser positivos, y el paso menor.")
        return np.arange(0.0, rmax + paso / 2.0, paso)

    @staticmethod
    def _html(ruta, titulo, parrafos, svg=""):
        if not ruta:
            return
        cuerpo = "".join("<p>%s</p>" % p for p in parrafos)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>%s</title></head>'
                    '<body style="font-family:sans-serif;max-width:760px;margin:1em auto">'
                    "<h2>%s</h2>%s%s<p style=\"color:#777\">Taller 3 · Estadística espacial · "
                    "herramientas %s</p></body></html>" % (titulo, titulo, cuerpo, svg, VERSION))

    @staticmethod
    def _campos(nombres):
        campos = QgsFields()
        for n in nombres:
            campos.append(QgsField(n, DOBLE))
        return campos

    @staticmethod
    def _valor(v):
        return None if v is None or not np.isfinite(v) else float(v)


# ---------------------------------------------------------------------
# T0 · Entorno
# ---------------------------------------------------------------------
class Entorno(_Base):
    DATOS, DOCUMENTO, LINEA = "DATOS", "DOCUMENTO", "LINEA"

    def name(self):
        return "entorno"

    def displayName(self):
        return "0 · Entorno y línea de identificación"

    def shortHelpString(self):
        return ("Imprime la versión de QGIS y de numpy, la huella del archivo de datos y la línea de "
                "entorno que va en la portada de la entrega. El enunciado dice qué huella tiene que salir: "
                "si no es esa, el archivo no es el del taller, y hay que descargarlo otra vez.")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.DATOS, "Archivo de datos del taller (taller3.gpkg)", extension="gpkg"))
        self.addParameter(QgsProcessingParameterString(
            self.DOCUMENTO, "Tu número de documento, sin puntos ni espacios"))
        self.addOutput(QgsProcessingOutputString(self.LINEA, "Línea de identificación"))

    def processAlgorithm(self, parameters, context, feedback):
        ruta = self.parameterAsFile(parameters, self.DATOS, context)
        doc = "".join(c for c in self.parameterAsString(parameters, self.DOCUMENTO, context) if c.isdigit())
        if len(doc) < 6:
            raise QgsProcessingException("El documento tiene que llevar al menos seis cifras.")
        if not os.path.isfile(ruta):
            raise QgsProcessingException("No encuentro el archivo de datos: " + ruta)
        h = hashlib.sha256()
        with open(ruta, "rb") as f:
            for trozo in iter(lambda: f.read(1 << 20), b""):
                h.update(trozo)
        huella = h.hexdigest()[:12]
        sello = hashlib.sha256(("T3|%s|%s" % (doc, huella)).encode()).hexdigest()[:8]
        linea = "T3 · doc %s · QGIS %s · numpy %s · datos %s · herramientas %s · sello %s" % (
            doc, Qgis.QGIS_VERSION.split("-")[0], np.__version__, huella, VERSION, sello)
        feedback.pushInfo("")
        feedback.pushInfo("COPIA ESTA LÍNEA EN LA PORTADA, TAL CUAL:")
        feedback.pushInfo(linea)
        feedback.pushInfo("")
        return {self.LINEA: linea}


# ---------------------------------------------------------------------
# T3 · Test de cuadrantes
# ---------------------------------------------------------------------
class Cuadrantes(_Base):
    NX, NY, SALIDA, INFORME = "NX", "NY", "SALIDA", "INFORME"

    def name(self):
        return "cuadrantes"

    def displayName(self):
        return "1 · Test de cuadrantes (χ²) sobre la ventana real"

    def shortHelpString(self):
        return ("Parte la caja de la ventana en NX × NY celdas, recorta cada celda con la ventana, cuenta "
                "los puntos de cada una y calcula el χ² de cuadrantes. El esperado de cada celda es "
                "proporcional a su área DENTRO de la ventana; las celdas que quedan fuera no existen. "
                "Es el `quadrat.test` del capítulo 4, módulos 5 y 6. Devuelve la rejilla recortada, con el "
                "observado, el esperado y el residuo de Pearson de cada celda.")

    def initAlgorithm(self, config=None):
        self._params_patron()
        self.addParameter(QgsProcessingParameterNumber(self.NX, "Columnas de la rejilla (NX)", defaultValue=4, minValue=2))
        self.addParameter(QgsProcessingParameterNumber(self.NY, "Filas de la rejilla (NY)", defaultValue=4, minValue=2))
        self.addParameter(QgsProcessingParameterFeatureSink(self.SALIDA, "Cuadrantes recortados"))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.INFORME, "Informe", "HTML (*.html)", optional=True, createByDefault=True))
        for k, t in (("N", "Puntos en la ventana"), ("CELDAS", "Celdas con área"), ("CHI2", "χ²"),
                     ("GL", "Grados de libertad"), ("P_DERECHA", "p, cola derecha"),
                     ("P_BILATERAL", "p bilateral"), ("ESPERADO_MIN", "Menor esperado")):
            self.addOutput(QgsProcessingOutputNumber(k, t))

    def processAlgorithm(self, parameters, context, feedback):
        x, y, anillos, w, a, crs = self._patron(parameters, context, feedback)
        nx = self.parameterAsInt(parameters, self.NX, context)
        ny = self.parameterAsInt(parameters, self.NY, context)
        cj = N.caja(anillos)
        ix, iy = N.celda_de(x, y, cj, nx, ny)
        obs = np.zeros((nx, ny))
        np.add.at(obs, (ix, iy), 1)
        dx, dy = (cj[1] - cj[0]) / nx, (cj[3] - cj[2]) / ny
        areas = np.zeros((nx, ny))
        geoms = {}
        for i in range(nx):
            for j in range(ny):
                celda = QgsGeometry.fromRect(QgsRectangle(
                    cj[0] + i * dx, cj[2] + j * dy, cj[0] + (i + 1) * dx, cj[2] + (j + 1) * dy))
                corte = celda.intersection(w)
                if corte is not None and not corte.isEmpty() and corte.area() > 0:
                    areas[i, j] = corte.area()
                    geoms[(i, j)] = corte
        if obs[areas == 0].sum() > 0:
            raise QgsProcessingException("Hay puntos en una celda sin área: la ventana no es válida.")
        x2, gl, esp = N.chi2_cuadrantes(obs.ravel(), areas.ravel())
        esp = esp.reshape(nx, ny)
        p_der = N.chi2_cola(x2, gl)
        p_bil = 2.0 * min(p_der, 1.0 - p_der)

        campos = QgsFields()
        campos.append(QgsField("columna", ENTERO))
        campos.append(QgsField("fila", ENTERO))
        for c in ("area_km2", "observado", "esperado", "residuo"):
            campos.append(QgsField(c, DOBLE))
        sink, destino = self.parameterAsSink(parameters, self.SALIDA, context, campos,
                                             QgsWkbTypes.MultiPolygon, crs)
        for (i, j), g in sorted(geoms.items()):
            f = QgsFeature(campos)
            g.convertToMultiType()
            f.setGeometry(g)
            f.setAttributes([i + 1, j + 1, areas[i, j] / 1e6, float(obs[i, j]), float(esp[i, j]),
                             float((obs[i, j] - esp[i, j]) / np.sqrt(esp[i, j]))])
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        emin = float(esp[areas > 0].min())
        lineas = ["Rejilla %d × %d sobre la caja de la ventana: %d celdas con área." % (nx, ny, gl + 1),
                  "χ² = %.5f con %d grados de libertad." % (x2, gl),
                  "p de la cola derecha = %.5g." % p_der,
                  "Índice de dispersión χ²/gl = %.5f." % (x2 / gl),
                  "Menor conteo esperado = %.5f." % emin]
        for s in lineas:
            feedback.pushInfo(s)
        ruta = self.parameterAsFileOutput(parameters, self.INFORME, context)
        self._html(ruta, "Test de cuadrantes", lineas)
        return {self.SALIDA: destino, self.INFORME: ruta, "N": len(x), "CELDAS": gl + 1, "CHI2": x2, "GL": gl,
                "P_DERECHA": p_der, "P_BILATERAL": p_bil, "ESPERADO_MIN": emin}


# ---------------------------------------------------------------------
# T3 · G, F y J
# ---------------------------------------------------------------------
class FuncionesGF(_Base):
    RMAX, PASO, LADO, R_LECTURA, SALIDA, INFORME = "RMAX", "PASO", "LADO", "R_LECTURA", "SALIDA", "INFORME"

    def name(self):
        return "gfj"

    def displayName(self):
        return "2 · Funciones G, F y J con corrección de borde"

    def shortHelpString(self):
        return ("G(r): fracción de puntos con su vecino más próximo a r o menos. F(r): fracción de sitios "
                "vacíos con un punto a r o menos. J = (1 − G)/(1 − F). Las tres con corrección de borde por "
                "muestra reducida: para cada r solo cuentan los puntos y los sitios a más de r del borde de "
                "la ventana. La curva teórica es la de un Poisson homogéneo con la intensidad del patrón. "
                "Capítulo 4, módulo 7.")

    def initAlgorithm(self, config=None):
        self._params_patron()
        self.addParameter(QgsProcessingParameterNumber(
            self.RMAX, "Radio máximo, en metros", QgsProcessingParameterNumber.Double, 600.0, minValue=1.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.PASO, "Paso de r, en metros", QgsProcessingParameterNumber.Double, 10.0, minValue=0.1))
        self.addParameter(QgsProcessingParameterNumber(
            self.LADO, "Sitios por lado de la rejilla de F", defaultValue=200, minValue=50, maxValue=600))
        self.addParameter(QgsProcessingParameterNumber(
            self.R_LECTURA, "Radio de lectura, en metros (0: ninguno)",
            QgsProcessingParameterNumber.Double, 0.0, minValue=0.0))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.SALIDA, "Tabla de G, F y J", QgsProcessing.TypeVector))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.INFORME, "Informe con la gráfica", "HTML (*.html)", optional=True, createByDefault=True))
        for k, t in (("N", "Puntos en la ventana"), ("SITIOS", "Sitios de F dentro de la ventana"),
                     ("G_R", "G en el radio de lectura"), ("F_R", "F en el radio de lectura"),
                     ("TEORICA_R", "Curva de Poisson en el radio de lectura"), ("J_R", "J en el radio de lectura")):
            self.addOutput(QgsProcessingOutputNumber(k, t))

    def processAlgorithm(self, parameters, context, feedback):
        x, y, anillos, w, a, crs = self._patron(parameters, context, feedback)
        rg = self._rg(self.parameterAsDouble(parameters, self.RMAX, context),
                      self.parameterAsDouble(parameters, self.PASO, context))
        lado = self.parameterAsInt(parameters, self.LADO, context)
        rl = self.parameterAsDouble(parameters, self.R_LECTURA, context)
        g = N.g_borde(x, y, anillos, rg)
        feedback.setProgress(30)
        f, sitios = N.f_borde(x, y, anillos, rg, lado)
        feedback.setProgress(90)
        teo = N.gf_teorica(len(x) / a, rg)
        j = N.j_de(g, f)

        campos = self._campos(["r", "G", "F", "poisson", "J"])
        sink, destino = self.parameterAsSink(parameters, self.SALIDA, context, campos,
                                             QgsWkbTypes.NoGeometry, crs)
        for fila in zip(rg, g, f, teo, j):
            ft = QgsFeature(campos)
            ft.setAttributes([self._valor(v) for v in fila])
            sink.addFeature(ft, QgsFeatureSink.FastInsert)

        res = {self.SALIDA: destino, "N": len(x), "SITIOS": sitios}
        lineas = ["%d puntos; %d sitios de la rejilla de F dentro de la ventana." % (len(x), sitios)]
        if rl > 0:
            q = int(np.argmin(np.abs(rg - rl)))
            if abs(rg[q] - rl) > 1e-9:
                raise QgsProcessingException("El radio de lectura tiene que ser un múltiplo del paso.")
            res.update({"G_R": self._valor(g[q]), "F_R": self._valor(f[q]),
                        "TEORICA_R": float(teo[q]), "J_R": self._valor(j[q])})
            lineas.append("En r = %g m: G = %.5f, F = %.5f, Poisson = %.5f, J = %.5f."
                          % (rl, g[q], f[q], teo[q], j[q]))
        for s in lineas:
            feedback.pushInfo(s)
        svg = N.svg_lineas(rg, [("G", g, VERDE, False), ("F", f, NARANJA, False), ("Poisson", teo, GRIS, True)],
                           "G y F frente a un Poisson homogéneo", "r (m)", "fracción",
                           marca=rl if rl > 0 else None)
        ruta = self.parameterAsFileOutput(parameters, self.INFORME, context)
        self._html(ruta, "Funciones G, F y J", lineas, svg)
        res[self.INFORME] = ruta
        return res


# ---------------------------------------------------------------------
# T3 · K y L de Ripley, con envolvente
# ---------------------------------------------------------------------
class RipleyKL(_Base):
    RMAX, PASO, NSIM, SEMILLA, R_LECTURA = "RMAX", "PASO", "NSIM", "SEMILLA", "R_LECTURA"
    SALIDA, INFORME = "SALIDA", "INFORME"

    def name(self):
        return "ripley"

    def displayName(self):
        return "3 · K y L de Ripley con envolvente de simulación"

    def shortHelpString(self):
        return ("K(r) con corrección de borde por muestra reducida, y L(r) = √(K/π), que bajo un Poisson "
                "homogéneo vale r. La envolvente es el mínimo y el máximo de L en NSIM patrones simulados "
                "con el mismo número de puntos repartidos al azar en la MISMA ventana. Con 99 simulaciones, "
                "salirse de la banda en un r fijado de antemano es un contraste al 2 %; recorrer la curva "
                "buscando dónde se sale no lo es. Capítulo 4, módulos 8, 10 y 11. La semilla hace que la "
                "banda sea la misma cada vez.")

    def initAlgorithm(self, config=None):
        self._params_patron()
        self.addParameter(QgsProcessingParameterNumber(
            self.RMAX, "Radio máximo, en metros", QgsProcessingParameterNumber.Double, 1000.0, minValue=1.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.PASO, "Paso de r, en metros", QgsProcessingParameterNumber.Double, 25.0, minValue=0.1))
        self.addParameter(QgsProcessingParameterNumber(
            self.NSIM, "Simulaciones de la envolvente (0: sin envolvente)", defaultValue=99, minValue=0, maxValue=999))
        self.addParameter(QgsProcessingParameterNumber(self.SEMILLA, "Semilla", defaultValue=2026, minValue=0))
        self.addParameter(QgsProcessingParameterNumber(
            self.R_LECTURA, "Radio de lectura, en metros (0: ninguno)",
            QgsProcessingParameterNumber.Double, 0.0, minValue=0.0))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.SALIDA, "Tabla de K y L", QgsProcessing.TypeVector))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.INFORME, "Informe con la gráfica", "HTML (*.html)", optional=True, createByDefault=True))
        for k, t in (("N", "Puntos en la ventana"), ("K_R", "K en el radio de lectura"),
                     ("L_MENOS_R", "L(r) − r en el radio de lectura"),
                     ("BANDA_INF", "Banda inferior de L(r) − r"), ("BANDA_SUP", "Banda superior de L(r) − r"),
                     ("USABLES_R", "Puntos a más de r del borde")):
            self.addOutput(QgsProcessingOutputNumber(k, t))

    def processAlgorithm(self, parameters, context, feedback):
        x, y, anillos, w, a, crs = self._patron(parameters, context, feedback)
        rg = self._rg(self.parameterAsDouble(parameters, self.RMAX, context),
                      self.parameterAsDouble(parameters, self.PASO, context))
        nsim = self.parameterAsInt(parameters, self.NSIM, context)
        semilla = self.parameterAsInt(parameters, self.SEMILLA, context)
        rl = self.parameterAsDouble(parameters, self.R_LECTURA, context)
        b = N.dist_borde(x, y, anillos)
        k = N.k_borde(x, y, b, a, rg)
        lr = N.l_de(k) - rg
        lo = hi = None
        if nsim > 0:
            feedback.pushInfo("Simulando %d patrones al azar en la ventana (semilla %d)…" % (nsim, semilla))
            lo, hi = N.envolvente_l(len(x), anillos, a, rg, nsim, semilla)
            lo, hi = lo - rg, hi - rg

        nombres = ["r", "K", "K_poisson", "L_menos_r"] + (["banda_inf", "banda_sup"] if nsim > 0 else [])
        campos = self._campos(nombres)
        sink, destino = self.parameterAsSink(parameters, self.SALIDA, context, campos,
                                             QgsWkbTypes.NoGeometry, crs)
        for q in range(len(rg)):
            fila = [rg[q], k[q], np.pi * rg[q] ** 2, lr[q]] + ([lo[q], hi[q]] if nsim > 0 else [])
            ft = QgsFeature(campos)
            ft.setAttributes([self._valor(v) for v in fila])
            sink.addFeature(ft, QgsFeatureSink.FastInsert)

        res = {self.SALIDA: destino, "N": len(x)}
        lineas = ["%d puntos; corrección de borde por muestra reducida." % len(x)]
        if rl > 0:
            q = int(np.argmin(np.abs(rg - rl)))
            if abs(rg[q] - rl) > 1e-9:
                raise QgsProcessingException("El radio de lectura tiene que ser un múltiplo del paso.")
            usables = int((b > rg[q]).sum())
            res.update({"K_R": self._valor(k[q]), "L_MENOS_R": self._valor(lr[q]), "USABLES_R": usables})
            lineas.append("En r = %g m: K = %.5f m², L(r) − r = %.5f m, con %d de %d puntos a más de r del borde."
                          % (rl, k[q], lr[q], usables, len(x)))
            if nsim > 0:
                res.update({"BANDA_INF": self._valor(lo[q]), "BANDA_SUP": self._valor(hi[q])})
                lineas.append("Banda de %d simulaciones en ese r: de %.5f a %.5f m."
                              % (nsim, lo[q], hi[q]))
        for s in lineas:
            feedback.pushInfo(s)
        svg = N.svg_lineas(rg, [("L(r) − r", lr, VERDE, False), ("Poisson", np.zeros(len(rg)), GRIS, True)],
                           "L(r) − r, con la banda de %d simulaciones" % nsim if nsim > 0 else "L(r) − r",
                           "r (m)", "L(r) − r (m)", banda=(lo, hi) if nsim > 0 else None,
                           marca=rl if rl > 0 else None)
        ruta = self.parameterAsFileOutput(parameters, self.INFORME, context)
        self._html(ruta, "K y L de Ripley", lineas, svg)
        res[self.INFORME] = ruta
        return res
