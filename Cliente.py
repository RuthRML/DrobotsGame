#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Lucia Calzado Piedrabuena
# Ruth Rodriguez-Manzaneque Lopez

import sys
import Ice
Ice.loadSlice('crobots.ice')
Ice.loadSlice('container.ice')
Ice.loadSlice('-I. --all robotFactory.ice')
import Services
import Container
import drobots
import math
import random

class Player(drobots.Player):
    def __init__(self, adapter, factorias, detector, containerRobots):
        self.adapter = adapter
        self.factorias = factorias
        self.factoriadetector = detector 
        self.container2 = containerRobots 
        self.contadorRobots = 0 
        self.contadorFactoria = 0 

    def makeController(self, bot, current=None):
        print("Creando un RobotController... con factoria "+str(self.contadorFactoria))
        robot = self.factorias[self.contadorFactoria].make(bot, self.contadorRobots)
        self.contadorFactoria= (self.contadorFactoria + 1) % 3
        self.contadorRobots=self.contadorRobots + 1

        # Introducir robots en Container
        self.container2.link(str(self.contadorRobots), robot)
        return robot

    def makeDetectorController(self, current=None):
        print("Creando un DetectorController...")
        detector = self.factoriadetector.makeDetector()
        return detector

    def win(self, current=None):
        print('Partida ganada.')
        current.adapter.getCommunicator().shutdown()

    def lose(self, current=None):
        print("Partida perdida.")
        current.adapter.getCommunicator().shutdown()

    def gameAbort(self, current=None):
        print("Abortando juego...");
        current.adapter.getCommunicator().shutdown()

class Cliente(Ice.Application):
    def run(self, argv):

        broker = self.communicator()
        adapter = broker.createObjectAdapter("PlayerAdapter")
        adapter2 = broker.createObjectAdapter("ContainerAdapter")

        containerRobots = Container.Container()

        # Factorias para controladores de robot
        factorias_robot_identity = ["RobotFactory1", "RobotFactory2", "RobotFactory3"]
        factorias_robot = []

        for factorias_identity in factorias_robot_identity:
            factory_proxy = broker.stringToProxy(factorias_identity)
            factorias_robot.append(drobots.RobotFactoryPrx.checkedCast(factory_proxy))

        # Factoria para controlador de detector
        detector_proxy = broker.stringToProxy("RobotFactory4")
        factoria_detector = drobots.DetectorFactoryPrx.checkedCast(detector_proxy)

        sirviente = Player(adapter, factorias_robot, factoria_detector, containerRobots)
        adapter2.add(containerRobots, broker.stringToIdentity("Robots"))

        proxyPlayer = adapter.add(sirviente, broker.stringToIdentity("Player"))
        proxyDirecto = adapter.createDirectProxy(proxyPlayer.ice_getIdentity())
        player = drobots.PlayerPrx.uncheckedCast(proxyDirecto)

        adapter.activate()
        adapter2.activate()

        proxyGame = broker.propertyToProxy("Game")
        game = drobots.GamePrx.checkedCast(proxyGame)

        idrandom = random.randint(0, 9999)
        game.login(player, str(idrandom))
        print("Partida comenzada.")

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()


Cliente().main(sys.argv)
