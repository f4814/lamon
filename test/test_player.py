import unittest
import sqlite3

from datetime import datetime

from lamon.player import Player, Players, PlayerNameError, PlayerStateError, \
                         PlayerIdentityError
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

    def test_score(self):
        """ Test addPoints and getScore """
        self.players.addPlayer('scorePlayer')

        score = 0
        for i in range(10,-5):
            self.players['scorePlayer'].addPoints(i, str(i))
            score += i

        progress = []
        for i in range(10,-5):
            progress.append(i)
            self.assertEqual(self.players['scorePlayer'].getScore(gameNames=i),
                        sum(i))

        self.assertEqual(self.players['scorePlayer'].getScore(), score)

    def test_identity(self):
        """ Test addIdentity and getNamName """
        self.players.addPlayer('identityPlayer')

        self.players['identityPlayer'].addIdentity({'id1': 'nick1',
                                                    'id2': 'nick2'})

        self.assertEqual(self.players['identityPlayer'].getName('id1'),
                         'nick1')
        self.assertEqual(self.players['identityPlayer'].getName('id2'),
                         'nick2')

        with self.assertRaises(PlayerIdentityError):
            self.players['identityPlayer'].addIdentity({'id1': 'nick1',
                                                        'id2': 'nick2'})

    def test_inGame(self):
        firstEnter = datetime(2000, 1, 1, hour=1)
        firstquit = datetime(2000, 1, 1, hour=2)
        secondEnter = datetime(2000, 1, 1, hour=5)
        secondquit = datetime(2000, 1, 1, hour=6)

        self.players.addPlayer('inGamePlayer')

        self.players['inGamePlayer'].enter("testgame", firstEnter)
        with self.assertRaises(PlayerStateError):
            self.players['inGamePlayer'].enter("testgame", firstEnter)

        self.players['inGamePlayer'].quit("testgame", firstquit)
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

    def test_inGame(self):
        """ Entering or leaving games two times in a row """
        self.players.addPlayer('inGameExceptionPlayer')

        self.players['inGameExceptionPlayer'].enter("exceptgame")
        with self.assertRaises(PlayerStateError):
            self.players['inGameExceptionPlayer'].enter('exceptgame')

        self.players['inGameExceptionPlayer'].quit('exceptgame')
        with self.assertRaises(PlayerStateError):
            self.players['inGameExceptionPlayer'].quit('exceptgame')

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
