import unittest
import sqlite3

from datetime import datetime

from lamon.player import Player, Players, PlayerNameError, PlayerStateError, \
                         PlayerNickError
from lamon.sql import initDatabase

class TestPlayerMethods(unittest.TestCase):
    def setUp(self):
        genericSetUp(self)

    def test_creation(self):
        """ Test creating players """
        with self.assertRaises(PlayerNameError):
            self.players['nonexistent']

        self.players.addPlayer('collisionPlayer')
        with self.assertRaises(PlayerNameError):
            self.players.addPlayer('collisionPlayer')

    def test_get(self):
        """ Test __getitem__ and getByNick """
        self.players.addPlayer('getitemPlayer0')
        self.players.addPlayer('getitemPlayer1')
        self.players.addPlayer('getByNickPlayer')

        stat = []
        for i in self.players:
            if i.name == 'getitemPlayer0' or i.name == 'getitemPlayer1':
                stat.append(i.name)

        self.assertTrue('getitemPlayer0' in stat and 'getitemPlayer1')

        self.players['getByNickPlayer'].addNick({'nickGame': 'nickPlayer'})
        nickPlayer = self.players.getByNick('nickGame', 'nickPlayer')
        self.assertTrue(nickPlayer.name == 'getByNickPlayer')

        with self.assertRaises(PlayerNameError):
            self.players['nonexistentPlayer']

        with self.assertRaises(IndexError):
            self.players['nonexistentPlayer']

        with self.assertRaises(PlayerNickError):
            self.players.getByNick('nonexistentGame', 'nonexistentPlayer')

    def test_score(self):
        """ Test addPoints and getScore """
        self.players.addPlayer('scorePlayer')
        games = "abcdefghijklmnopqrstuvwxyz"

        score = 0
        for i in range(-5,10):
            self.players['scorePlayer'].addPoints(i, games[i])
            score += i

        progress = []
        for i in range(-5,10):
            progress.append(i)
            self.assertEqual(self.players['scorePlayer'].getScore(
                             gameNames=[games[i]]), i)

        self.assertEqual(self.players['scorePlayer'].getScore(), score)

    def test_identity(self):
        """ Test addNick, hasNick, getNick"""
        self.players.addPlayer('identityPlayer')

        self.assertFalse(self.players['identityPlayer'].hasNick('id1'))
        self.players['identityPlayer'].addNick({'id1': 'nick1',
                                                'id2': 'nick2'})
        self.assertTrue(self.players['identityPlayer'].hasNick('id1'))

        self.assertEqual(self.players['identityPlayer'].getNick('id1'),
                         'nick1')
        self.assertEqual(self.players['identityPlayer'].getNick('id2'),
                         'nick2')

        with self.assertRaises(PlayerNickError):
            self.players['identityPlayer'].addNick({'id1': 'nick1',
                                                    'id2': 'nick2'})

    def test_inGame(self):
        firstEnter = datetime(2000, 1, 1, hour=1)
        firstquit = datetime(2000, 1, 1, hour=2)
        secondEnter = datetime(2000, 1, 1, hour=5)
        secondquit = datetime(2000, 1, 1, hour=6)

        self.players.addPlayer('inGamePlayer')

        self.players['inGamePlayer'].enter("testgame", firstEnter)
        self.assertTrue(self.players['inGamePlayer'].inGame('testgame'))
        with self.assertRaises(PlayerStateError):
            self.players['inGamePlayer'].enter("testgame", firstEnter)

        self.players['inGamePlayer'].quit("testgame", firstquit)
        self.assertFalse(self.players['inGamePlayer'].inGame('testgame'))
        with self.assertRaises(PlayerStateError):
            self.players['inGamePlayer'].quit("testgame", firstEnter)

        self.assertEqual(self.players['inGamePlayer'].getTimeInGame(),
                         3600)

        self.players['inGamePlayer'].enter("testgame2", secondEnter)
        self.players['inGamePlayer'].quit("testgame2", secondquit)
        self.assertEqual(
            self.players['inGamePlayer'].getTimeInGame(['testgame2']),
            3600)
        self.assertEqual(self.players['inGamePlayer'].getTimeInGame(),
                         7200)

    def tearDown(self):
        genericTearDown(self)


def genericSetUp(self):
    self.sqlConn = sqlite3.connect(":memory:")
    cursor = self.sqlConn.cursor()
    initDatabase(cursor)
    self.players = Players(self.sqlConn)

def genericTearDown(self):
    self.sqlConn.close()

if __name__ == '__main__':
    unittest.main()
