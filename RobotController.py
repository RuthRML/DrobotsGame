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

class RobotFactory(drobots.RobotFactory):
    self.detector = None

    def make(self, bot, contador, current=None):
        if (bot.ice_isA("::drobots::Attacker")):
            sirviente = RobotControllerAtaque(bot, contador)
        elif (bot.ice_isA("::drobots::Defender")):
            sirviente = RobotControllerDefensa(bot, contador)
        proxy = current.adapter.addWithUUID(sirviente)
        proxyDirecto = current.adapter.createDirectProxy(proxy.ice_getIdentity())
        robot=drobots.RobotControllerPrx.checkedCast(proxyDirecto)
        return robot

    def makeDetector(self, current=None):
        if (detector == None):
            sirviente = DetectorController()
            proxy_detector = current.adapter.addWithUUID(sirviente)
            proxyDirecto = current.adapter.createDirectProxy(proxy_detector.ice_getIdentity())
            self.detector = drobots.DetectorControllerPrx.checkedCast(proxyDirecto)
        return self.detector

class RobotControllerDefensa(drobots.RobotController, drobotsCoordinados.Coordinacion):
    def __init__(self, bot, contador):
        self.robot = bot
        self.turnos = 0
        self.angulo = 0
        self.id = contador
        print("Robot de defensa creado.")

    def turn(self, current=None):
        self.turnos = self.turnos+1
        print ("Turno" + self.turnos)
        proxyContainer = current.adapter.getCommunicator().stringToProxy("Robots")
        container = Services.ContainerPrx.checkedCast(proxyContainer)
        async = container.begin_listCoordinar()
        robots = container.end_listCoordinar(async)
        if(self.robot.damage()==100):
            self.robotDestroyed()
        else:
            print("Escaneando...")
            self.angulo = int(math.degrees(random.randint(0,359)) % 360.0)
            wide = random.randint(1,20)
            robotsencontrados = self.robot.scan(self.angulo, wide)
            if(robotsencontrados>0):
                print("Enemigo(s) encontrado.")
                atac = drobots2.CoordinacionPrx.uncheckedCast(robots["3"]) # Robot de ataque key = 3
                atac2 = drobots2.CoordinacionPrx.uncheckedCast(robots["4"]) # Robot de ataque key = 4
                atac.EnemigoDetectado(self.angulo)
                atac2.EnemigoDetectado(self.angulo)
            elif(robotsencontrados==0 and self.robot.energy()>=62):
                xdestino = random.randint(10,399)
                ydestino = random.randint(10,399)
                coordenadasactuales = self.robot.location()
                xrelativo = xdestino - coordenadasactuales.x
                yrelativo = ydestino - coordenadasactuales.y
                distancia = math.hypot(xrelativo, yrelativo)
                print("Cambiando posición a una distancia de %s" % distancia)
                nuevoangulo = int(math.degrees(math.atan2(xrelativo, yrelativo)) % 360.0)
                velocidad = 100
                if(distancia < 10):
                    velocidad = max(min(100, self.robot.speed() / (10 - distancia)), 1)
                if(distancia > 0):
                    self.robot.drive(nuevoangulo, velocidad)
                else:
                    self.robot.drive(0,0)
                    return

    def robotDestroyed(self, current=None):
        print("Robot destruido.")

    def EnemigoDetectado(self, anguloenemigo,  current=None):
        None

    def PosicionDetector(self, destino, current=None):
        None

class RobotControllerAtaque(drobots.RobotController, drobotsCoordinados.Coordinacion):
    def __init__(self, bot, contador):
        self.robot = bot
        self.turnos = 0
        self.angulo = 0
        self.id = contador
        print("Robot de ataque creado.")

    def turn(self, current=None):
        self.turnos = self.turnos + 1
        print ("Turno" + self.turnos)
        if(self.robot.damage()==100):
            self.robotDestroyed()
        else:
            print("Atacando...")
            distancia = random.randint(0,200)
            if(self.angulo==0):
                self.angulo = int(math.degrees(random.randint(0,359)) % 360.0)
            self.robot.cannon(self.angulo, distancia)
            if(self.robot.energy()>=62):
                xdestino = random.randint(10,399)
                ydestino = random.randint(10,399)
                coordenadasactuales = self.robot.location()
                xrelativo = xdestino - coordenadasactuales.x
                yrelativo = ydestino - coordenadasactuales.y
                distancia = math.hypot(xrelativo, yrelativo)
                print("Cambiando posición a una distancia de %s" % distancia)
                nuevoangulo = int(math.degrees(math.atan2(xrelativo, yrelativo)) % 360.0)
                velocidad = 100
                if(distancia < 10):
                    velocidad = max(min(100, self.robot.speed() / (10 - distancia)), 1)
                if(distancia>0):
                    self.robot.drive(nuevoangulo,velocidad)
                else:
                    self.robot.drive(0,0)
                    return

    def robotDestroyed(self, current=None):
        print("Robot destruido.")

    def EnemigoDetectado(self, anguloenemigo, current=None):
        print("Enemigo(s) detectado(s)")
        self.angulo=anguloenemigo

    def PosicionDetector(self, destino, current=None):
        print("Enemigo(s) detectado(s)")
        xdestino = destino.x
        ydestino = destino.y
        coordenadasactuales = self.robot.location()
        xrelativo = xdestino - coordenadasactuales.x
        yrelativo = ydestino - coordenadasactuales.y
        anguloenemigos = int(math.degrees(math.atan2(xrelativo, yrelativo)) % 360.0)
        self.angulo = anguloenemigos

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
        for bot in robots:
            for x in list(rango_x):
                for y in list(rango_y):
                    posicion_relativa.x = posicion_relativa.x + 1
                    posicion_relativa.y = posicion_relativa.y + 1
                    if(posicion_relativa == bot.location()):
                        flag = False
        if flag:
            ataque = drobots2.CoordinacionPrx.uncheckedCast(robots["3"]) # Robot de ataque key = 3
            ataque2 = drobots2.CoordinacionPrx.uncheckedCast(robots["4"]) # Robot de ataque key = 4
            ataque.PosicionDetector(posicion)
            ataque2.PosicionDetector(posicion)

class Nodo(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        sirviente = RobotFactory()

        adapter = broker.createObjectAdapter("FactoriaAdapter")
        
        identity = broker.getProperties().getProperty("Identity")
        factoria = adapter.add(sirviente, broker.stringToIdentity(identity))
        proxycontainer = broker.stringToProxy("Container")
        container = Services.ContainerPrx.uncheckedCast(proxycontainer)

        adapter.activate()
        container.link(str(random.randint(1,50)),factoria)

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

Nodo().main(sys.argv)
