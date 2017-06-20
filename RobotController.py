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

class RobotFactory(drobots.RobotFactory):
    def __init__(self):
        self.detector = None

    def make(self, bot, contador, current=None):
        if(bot.ice_isA("::drobots::Attacker")):
            sirviente = RobotControllerAtaque(bot, contador)
        elif(bot.ice_isA("::drobots::Defender")):
            sirviente = RobotControllerDefensa(bot, contador)
        else:
            sirviente = RobotControllerBase(bot, contador)
        proxy = current.adapter.addWithUUID(sirviente)
        proxyDirecto = current.adapter.createDirectProxy(proxy.ice_getIdentity())
        robot = drobots.RobotControllerPrx.uncheckedCast(proxyDirecto)
        return robot

class RobotControllerBase(drobots.RobotController, drobotsCoordinados.Coordinacion):
    def __init__(self, bot, contador):
        self.robot = bot
        self.turnos = 0
        self.angulo = 0
        self.id = contador
        self.posicionactual = drobots.Point(0,0)
        print("Robot"+str(self.id)+" genérico creado.")

    def turn(self, current=None):
        self.turnos = self.turnos+1
        self.posicionactual = self.robot.location()
        proxyContainer = current.adapter.getCommunicator().stringToProxy("Robots")
        container = Services.ContainerPrx.checkedCast(proxyContainer)
        async = container.begin_listCoordinar()
        robots = container.end_listCoordinar(async)
        if(self.robot.damage()==100):
            self.robotDestroyed()
        else:
            print("Robot"+str(self.id)+" escaneando...")
            self.angulo = int(math.degrees(random.randint(0,359)) % 360.0)
            wide = random.randint(1,20)
            robotsencontrados = self.robot.scan(self.angulo, wide)
            if(robotsencontrados>0):
                atac = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["3"]) # Robot de ataque key = 3
                atac2 = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["4"]) # Robot de ataque key = 4
                atac.enemigoDetectado(self.angulo)
                atac2.enemigoDetectado(self.angulo)
                print("Robot"+str(self.id)+" atacando...")
                distancia = random.randint(0,200)
                self.robot.cannon(self.angulo, distancia)
            elif(robotsencontrados==0 and self.robot.energy()>=61):
                xdestino = random.randint(10,399)
                ydestino = random.randint(10,399)
                coordenadasactuales = self.posicionactual
                xrelativo = xdestino - coordenadasactuales.x
                yrelativo = ydestino - coordenadasactuales.y
                distancia = math.hypot(xrelativo, yrelativo)
                print("Robot"+str(self.id)+" cambiando posición a una distancia de %s" % distancia)
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
        print("Robot"+str(self.id)+" destruido.")

    def enemigoDetectado(self, anguloenemigo, current=None):
        print("Coordinacion: Robot"+str(self.id)+" girando hacia los enemigo(s) detectado(s)")
        self.angulo=anguloenemigo
        if(self.robot.energy() >= 51):
            self.robot.cannon(self.angulo, 100)

    def posicionDetector(self, posx, posy, current=None):
        print("Alerta! Enemigo(s) detectado(s)")
        xdestino = posx
        ydestino = posy
        coordenadasactuales = self.posicionactual
        xrelativo = xdestino - coordenadasactuales.x
        yrelativo = ydestino - coordenadasactuales.y
        anguloenemigos = int(math.degrees(math.atan2(xrelativo, yrelativo)) % 360.0)
        self.angulo = anguloenemigos
        if(self.robot.energy() >= 51):
            self.robot.cannon(self.angulo, 100)

    def localizacionx(self, current=None):
        return self.posicionactual.x

    def localizaciony(self, current=None):
        return self.posicionactual.y

class RobotControllerDefensa(drobots.RobotController, drobotsCoordinados.Coordinacion):
    def __init__(self, bot, contador):
        self.robot = bot
        self.turnos = 0
        self.angulo = 0
        self.id = contador
        self.posicionactual = drobots.Point(0,0)
        print("Robot"+str(self.id)+" de defensa creado.")

    def turn(self, current=None):
        self.turnos = self.turnos+1
        self.posicionactual = self.robot.location() 
        proxyContainer = current.adapter.getCommunicator().stringToProxy("Robots")
        container = Services.ContainerPrx.checkedCast(proxyContainer)
        async = container.begin_listCoordinar()
        robots = container.end_listCoordinar(async)
        if(self.robot.damage()==100): 
            self.robotDestroyed()
        else:
            print("Robot"+str(self.id)+" escaneando...")
            self.angulo = int(math.degrees(random.randint(0,359)) % 360.0)
            wide = random.randint(1,20)
            robotsencontrados = self.robot.scan(self.angulo, wide) 
            if(robotsencontrados>0):
                print("Robot"+str(self.id)+" ha encontrado enemigo(s).")
                atac = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["3"]) # Robot de ataque key = 3
                atac2 = drobotsCoordinados.CoordinacionPrx.uncheckedCast(robots["4"]) # Robot de ataque key = 4
                atac.enemigoDetectado(self.angulo)
                atac2.enemigoDetectado(self.angulo)
            elif(robotsencontrados==0 and self.robot.energy()>=61):
                xdestino = random.randint(10,399)
                ydestino = random.randint(10,399)
                coordenadasactuales = self.posicionactual
                xrelativo = xdestino - coordenadasactuales.x
                yrelativo = ydestino - coordenadasactuales.y
                distancia = math.hypot(xrelativo, yrelativo)
                print("Robot"+str(self.id)+"cambiando posición a una distancia de %s" % distancia)
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
        print("Robot"+str(self.id)+" destruido.")

    def enemigoDetectado(self, anguloenemigo,  current=None):
        None

    def posicionDetector(self, posx, posy, current=None):
        None

    def localizacionx(self, current=None):
        return self.posicionactual.x

    def localizaciony(self, current=None):
        return self.posicionactual.y

class RobotControllerAtaque(drobots.RobotController, drobotsCoordinados.Coordinacion):
    def __init__(self, bot, contador):
        self.robot = bot
        self.turnos = 0
        self.angulo = 0
        self.id = contador
        self.posicionactual = drobots.Point(0,0)
        print("Robot"+str(self.id)+" de ataque creado.")

    def turn(self, current=None):
        self.turnos = self.turnos + 1
        self.posicionactual = self.robot.location()
        if(self.robot.damage()==100):
            self.robotDestroyed()
        else:
            print("Robot"+str(self.id)+" atacando...")
            distancia = random.randint(0,200)
            if(self.angulo==0):
                self.angulo = int(math.degrees(random.randint(0,359)) % 360.0)
            self.robot.cannon(self.angulo, distancia)
            return
            #if(self.robot.energy()>=61):
                #xdestino = random.randint(10,399)
                #ydestino = random.randint(10,399)
                #coordenadasactuales = self.posicionactual
                #xrelativo = xdestino - coordenadasactuales.x
                #yrelativo = ydestino - coordenadasactuales.y
                #distancia = math.hypot(xrelativo, yrelativo)
                #print("Robot"+str(self.id)+" cambiando posición a una distancia de %s" % distancia)
                #nuevoangulo = int(math.degrees(math.atan2(xrelativo, yrelativo)) % 360.0)
                #velocidad = 100
                #if(distancia < 10):
                    #velocidad = max(min(100, self.robot.speed() / (10 - distancia)), 1)
                #if(distancia>0):
                    #self.robot.drive(nuevoangulo,velocidad)
                #else:
                    #self.robot.drive(0,0)
                    #return

    def robotDestroyed(self, current=None):
        print("Robot"+str(self.id)+" destruido.")

    def enemigoDetectado(self, anguloenemigo, current=None):
        print("Coordinacion: Robot"+str(self.id)+" girando hacia los enemigo(s) detectado(s)")
        self.angulo=anguloenemigo
        if(self.robot.energy() >= 51):
            self.robot.cannon(self.angulo, 100)

    def posicionDetector(self, posx, posy, current=None):
        print("Alerta! Enemigo(s) detectado(s)")
        xdestino = posx
        ydestino = posy
        coordenadasactuales = self.posicionactual
        xrelativo = xdestino - coordenadasactuales.x
        yrelativo = ydestino - coordenadasactuales.y
        anguloenemigos = int(math.degrees(math.atan2(xrelativo, yrelativo)) % 360.0)
        self.angulo = anguloenemigos
        if(self.robot.energy() >= 51):
            self.robot.cannon(self.angulo, 100)

    def localizacionx(self, current=None):
        return self.posicionactual.x

    def localizaciony(self, current=None):
        return self.posicionactual.y

class Nodo(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        sirviente = RobotFactory()

        adapter = broker.createObjectAdapter("FactoriaAdapter")
        
        identity = broker.getProperties().getProperty("Identity")
        factoria = adapter.add(sirviente, broker.stringToIdentity(identity))
        #proxycontainer = broker.stringToProxy("Container")
        #container = Services.ContainerPrx.uncheckedCast(proxycontainer)

        adapter.activate()
        #container.link(str(random.randint(1,50)),factoria)

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

Nodo().main(sys.argv)
