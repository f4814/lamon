import unittest
import sqlite3

from lamon.game.source import Source
from lamon.game import GameConnectionError
from lamon.player import Players

class TestSourceExceptions(unittest.TestCase):
    def setUp(self):
        self.sqlConn = sqlite3.connect(':memory:')
        players = Players(self.sqlConn)
        config = {'ip': '127.0.0.1', 'port': 6582, 'delay': 1}

        self.game = SourceDummy(players, config)

    def test_connectionError(self):
        """ Raising GameConnectionError on connection failure """
        self.assertRaises(GameConnectionError, self.game.connect)
        self.assertRaises(GameConnectionError, self.game.getPlayerScores)

    def tearDown(self):
        self.game.close()
        self.sqlConn.close()

class SourceDummy(Source):
    def __init__(self, players, config):
        super().__init__(players, config)
        self.name = 'SourceTester'
        self.internalName = 'SourceTester'
