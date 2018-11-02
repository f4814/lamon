import unittest
import sqlite3

from lamon.game import Game
from lamon.player import Players
from lamon.sql import initDatabase

class GameDummy(Game):
    """ Quick and dirty dummy game """
    def __init__(self, players, sqlConn):
        self.sqlConn = sqlConn
        self._config = { 'ip': '', 'port': '', 'delay': '' }
        super().__init__(players, self._config)
        self.name = "dummy"

    def connect(self):
        raise TestException('Dummy Game can not connect')

    def getPlayerScores(self):
        _scores = {'dummy1': 0, 'dummy2': 0, 'dummy3': 0}
        if self._scores == {}:
            self.players.addPlayer('testPlayer1')
            self.players.addPlayer('testPlayer2')
            self.players.addPlayer('testPlayer3')

            self.players['testPlayer1'].addNick({self.name: 'dummy1'})
            self.players['testPlayer2'].addNick({self.name: 'dummy2'})
            self.players['testPlayer3'].addNick({self.name: 'dummy3'})
        else:
            _scores['dummy1'] += 1
            _scores['dummy2'] += 2
            _scores['dummy3'] += 3

        return _scores

    def close(self):
        raise TextException('Dummy Game can not close connection')


class TestGame(unittest.TestCase):
    def setUp(self):
        self.sqlConn = sqlite3.connect(':memory:')
        initDatabase(self.sqlConn.cursor())
        self.players = Players(self.sqlConn)
        self.game = GameDummy(self.players, self.sqlConn)

    def test_updatePlayers(self):
        """ Test player update mechanism """
        self.game.updatePlayers()

        p1 = self.players['testPlayer1'].getScore()
        p2 = self.players['testPlayer2'].getScore(gameNames=['dummy'])
        p3 = self.players['testPlayer3'].getScore()

        self.game.updatePlayers()

        p1_ = self.players['testPlayer1'].getScore()
        p2_ = self.players['testPlayer2'].getScore(gameNames=['dummy'])
        p3_ = self.players['testPlayer3'].getScore()

        self.assertEqual(p1 + 1, p1_)
        self.assertEqual(p2 + 2, p2_)
        self.assertEqual(p3 + 3, p3_)

    def tearDown(self):
        self.sqlConn.close()


class TestException(Exception):
    pass
