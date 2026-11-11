# -*- coding: utf-8 -*-
from qgis.core import QgsProcessingProvider

from .algoritmos import Entorno, Cuadrantes, FuncionesGF, RipleyKL


class ProveedorTaller3(QgsProcessingProvider):
    def id(self):
        return "taller3"

    def name(self):
        return "Taller 3 · Estadística espacial"

    def longName(self):
        return self.name()

    def loadAlgorithms(self):
        for alg in (Entorno, Cuadrantes, FuncionesGF, RipleyKL):
            self.addAlgorithm(alg())
