#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Lucia Calzado Piedrabuena
# Ruth Rodriguez-Manzaneque Lopez

import sys
import Ice
Ice.loadSlice('crobots.ice')
Ice.loadSlice('container.ice')
Ice.loadSlice('coordinacion.ice')
Ice.loadSlice('-I. --all robotFactory.ice')
import drobots
import Services
import drobotsCoordinados
import math
import random

class DetectorFactory(drobots.DetectorFactory):
    def __init__(self):
        self.detector = None

    def makeDetector(self, current=None):
        if (self.detector == None):
            sirviente = DetectorController()
            proxy_detector = current.adapter.addWithUUID(sirviente)
            proxyDirecto = current.adapter.createDirectProxy(proxy_detector.ice_getIdentity())
            self.detector = drobots.DetectorControllerPrx.checkedCast(proxyDirecto)
        return self.detector

class DetectorController(drobots.DetectorController, drobotsCoordinados.Coordinacion):
    def __init__(self, current=None):
        print("Detector creado.")

    def alert(self, posicion, enemigos, current=None):
        flag = True
        posicion_relativa = posicion
        derecha_x = posicion.x-80
        izquierda_x = posicion.x+80
        derecha_y = posicion.y-80
        izquierda_y = posicion.y+80

        rango_x = range(derecha_x, izquierda_x)
        rango_y = range(derecha_y, izquierda_y)

        proxyContainer = current.adapter.getCommunicator().stringToProxy("Robots")
        container = Services.ContainerPrx.checkedCast(proxyContainer)
        async = container.begin_listCoordinar()
        robots = container.end_listCoordinar(async)

        defensa = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["1"]) # Robot de defensa key = 1
        defensa2 = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["2"]) # Robot de defensa key = 2
        ataque = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["3"]) # Robot de ataque key = 3
        ataque2 = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["4"]) # Robot de ataque key = 4
        #for bot in robots:
        for x in list(rango_x):
            for y in list(rango_y):
                posicion_relativa.x = posicion_relativa.x + 1
                posicion_relativa.y = posicion_relativa.y + 1
                if(posicion_relativa.x == defensa.localizacionx() and posicion_relativa.y == defensa.localizaciony()):
                    flag = False
                elif(posicion_relativa.x == defensa2.localizacionx() and posicion_relativa.y == defensa2.localizaciony()):
                    flag = False
                elif(posicion_relativa.x == ataque.localizacionx() and posicion_relativa.y == ataque.localizaciony()):
                    flag = False
                elif(posicion_relativa.x == ataque2.localizacionx() and posicion_relativa.y == ataque2.localizaciony()):
                    flag = False
        if flag == True:
            #ataque = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["3"]) # Robot de ataque key = 3
            #ataque2 = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["4"]) # Robot de ataque key = 4
            ataque.posicionDetector(posicion.x, posicion.y)
            ataque2.posicionDetector(posicion.x, posicion.y)

class Nodo(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        sirviente = DetectorFactory()

        adapter = broker.createObjectAdapter("FactoriaAdapter")
        
        #identity = broker.getProperties().getProperty("Identity")
        #factoria = adapter.add(sirviente, broker.stringToIdentity(identity))
        factoria = adapter.add(sirviente, broker.stringToIdentity("RobotFactory4"))
        #proxycontainer = broker.stringToProxy("Container")
        #container = Services.ContainerPrx.uncheckedCast(proxycontainer)

        adapter.activate()
        #container.link(str(random.randint(1,50)),factoria)

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

Nodo().main(sys.argv)
