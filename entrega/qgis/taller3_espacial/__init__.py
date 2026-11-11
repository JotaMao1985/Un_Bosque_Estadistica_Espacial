# -*- coding: utf-8 -*-
"""Complemento del Taller 3 de Estadística Espacial: solo registra el proveedor."""


class Taller3:
    def __init__(self, iface=None):
        self.proveedor = None

    def initProcessing(self):
        from qgis.core import QgsApplication
        from .proveedor import ProveedorTaller3
        self.proveedor = ProveedorTaller3()
        QgsApplication.processingRegistry().addProvider(self.proveedor)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        from qgis.core import QgsApplication
        if self.proveedor is not None:
            QgsApplication.processingRegistry().removeProvider(self.proveedor)
            self.proveedor = None


def classFactory(iface):
    return Taller3(iface)
