#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Lucia Calzado Piedrabuena
# Ruth Rodriguez-Manzaneque Lopez

import sys
import Ice
Ice.loadSlice('crobots.ice')
Ice.loadSlice('container.ice')
import Services
import Container
import drobots
import math
import random

class Player(drobots.Player):
    def __init__(self, adapter, containerFactorias, containerRobots):
        self.adapter = adapter
        self.container = containerFactorias # Container de factorias.
        self.container2 = containerRobots # Container de robots.
        self.contadorRobots = 0 # Contador para id de robot.
        self.contadorFactoria = 0 # Contado para factorias.

    def makeController(self, bot, current=None):
        print("Creando un RobotController...")
        proxiesContainer, keys=self.container.list()
        factoriarobot = drobots.RobotFactoryPrx.uncheckedCast(proxiesContainer[keys[self.contadorFactoria]])
        if self.contadorFactoria<2: # Tenemos 3 factorias
            self.contadorFactoria= self.contadorFactoria + 1
        self.contadorRobots=self.contadorRobots + 1
        robot = factoriarobot.make(bot, self.contadorRobots)
        self.container2.link(str(self.contadorRobots), robot)
        return robot

    def makeDetectorController(self, current=None):
        print("Creando un DetectorController...")
        proxiesContainer, keys=self.container.list()
        factoriaDetector = drobots.DetectorFactoryPrx.uncheckedCast(proxiesContainer[keys[self.contadorFactoria]])
        detector = factoriaDetector.make()
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

        containerFactorias = Container.Container()
        containerRobots = Container.Container()

        sirviente = Player(adapter, containerFactorias, containerRobots)
        adapter2.add(containerFactorias, broker.stringToIdentity("Container"))
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
