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
    def make(self, bot, contador, current=None):
        if (bot.ice_isA("::drobots::Attacker")):
            sirviente = RobotControllerAtaque(bot, contador)
        elif (bot.ice_isA("::drobots::Defender")):
            sirviente = RobotControllerDefensa(bot, contador)
        proxy = current.adapter.addWithUUID(sirviente)
        proxyDirecto = current.adapter.createDirectProxy(proxy.ice_getIdentity())
        robot=drobots.RobotControllerPrx.checkedCast(proxyDirecto)
        return robot

class RobotControllerDefensa(drobots.RobotController, drobotsCoordinados.Coordinacion):
    def __init__(self, bot, contador):
        self.robot = bot
        self.turnos = 0
        self.angulo = 0
        self.id = contador
        print("Robot de defensa creado.")

    def turn(self, current=None):
        self.turnos = self.turnos+1
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
                #x = coordenadasactuales.x
                #y = coordenadasactuales.y
                xrelativo = xdestino - coordenadasactuales.x
                yrelativo = ydestino - coordenadasactuales.y
                #distancia = int(math.sqrt((x-xmov)**2+(y-ymov)**2))
                distancia = math.hypot(xrelativo, yrelativo)
                print("Cambiando posición a %s" % distancia)
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

    def EnemigoDetectado(self, anguloenemigo,  current=None):
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
                #x = coordenadasactuales.x
                #y = coordenadasactuales.y
                xrelativo = xdestino - coordenadasactuales.x
                yrelativo = ydestino - coordenadasactuales.y
                #distancia = int(math.sqrt((x-xmov)**2+(y-ymov)**2))
                distancia = math.hypot(xrelativo, yrelativo)
                print("Cambiando posición a %s" % distancia)
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
        print("Enemigo detectado")
        self.angulo=anguloenemigo

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
