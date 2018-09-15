import unittest
import sqlite3

from lamon.player import Player, Players, PlayerNameError
from lamon.sql import initDatabase

class TestPlayerMethods(unittest.TestCase):
    def setUp(self):
        genericSetUp(self)

    def test_score(self):
        """ Test addPoints and getScore """
        self.players.addPlayer('scorePlayer')

        score = 0
        for i in range(10,-5):
            self.players['scorePlayer'].addPoints(i, str(i))
            score += 0

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

    def tearDown(self):
        genericTearDown(self)


class TestPlayerException(unittest.TestCase):
    def setUp(self):
        genericSetUp(self)
    def test_nonexistent(self):
        """ Indexing an non-existent player """
        with self.assertRaises(PlayerNameError):
            self.players['nonexistent']

    def test_collision(self):
        """ Creating an already existent player """
        self.players.addPlayer('collisionPlayer')
        self.assertRaises(PlayerNameError,
                          self.players.addPlayer, 'collisionPlayer')

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
