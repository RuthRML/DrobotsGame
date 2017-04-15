#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Lucia Calzado Piedrabuena
# Ruth Rodriguez-Manzaneque Lopez

import sys
import Ice
Ice.loadSlice('crobots.ice')
Ice.loadSlice('container.ice')
Ice.loadSlice('coordinacion.ice')
import drobots
import Services
import drobotsCoordinados
import math
import random

class DetectorFactory(drobots.RobotFactory):
    self.detector

    def make(self, current=None):
        if (detector == None):
            sirviente = DetectorController()
            proxy_detector = current.adapter.addWithUUID(sirviente)
            proxyDirecto = current.adapter.createDirectProxy(proxy_detector.ice_getIdentity())
            self.detector = drobots.DetectorControllerPrx.checkedCast(proxyDirecto)
        return self.detector

class DetectorController(drobots.DetectorController):
    def __init__(self, current=None):
        print("Detector creado.")

    def alert(self, posicion, enemigos, current=None):

