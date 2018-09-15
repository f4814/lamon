"""
Player Abstractions
"""
import sqlite3

from datetime import datetime

class Player():
    """
    A player and set of identities on the servers
    Player objects are created by the Players object and should only be used
    for one task.
    """
    def __init__(self, name, cursor, identities=None):
        self.name = name
        self.cursor = cursor

        # Add player to database if not already existent
        query = "SELECT * FROM player WHERE name=?"
        add = "INSERT INTO player VALUES(?)"

        if not cursor.execute(query, (name,)).fetchone():
            cursor.execute(add, (name,))
            cursor.connection.commit()

        # Add identities
        if identities:
            self.addIdentity(identities)

    def addIdentity(self, identity):
        """
        Add a identity to the Player
        :param identity: Identity dict
        :type identity: dict
        """
        print(identity)
        add = "INSERT INTO identity VALUES (?,?,?)"
        for game, nick in identity.items():
            self.cursor.execute(add, (game, nick, self.name))
        self.cursor.connection.commit()

    def getName(self, gameName):
        """ Find the nickname in game """
        query = """"
            SELECT gameName FROM identity WHERE gameName='?' AND playerName='?'
            """
        self.cursor.execute(query, gameName, self.name)
        return self.cursor.fetchone()

    def getScore(self, gameNames=None):
        """
        Get the score of a player
        :param gameNames: List of games to read the score from. None is all
        :returns: Int score
        """
        score = 0
        querySimple = "SELECT points FROM scoreUpdates WHERE playerName='?'"
        queryMany = """
            SELECT points FROM scoreUpdates
                WHERE gameName REGEXP '?'
                AND playerName='?'
            """

        if gameNames:
            scores = self.cursor.execute(queryMany, '|'.join(gameNames),
                                         self.name)
        else:
            scores = self.cursor.execute(querySimple, self.name)

        for s in scores:
            score += s

        return score

    def addPoints(self, points, gameName):
        """
        Add points to player.
        :param points: Int gained points
        :param gameName: Name of the game
        """
        query = "INSERT INTO scoreUpdate (?, ?, ?, ?)"
        self.cursor.execute(query, points, str(datetime.now()),
                            gameName, self.name)
        self.cursor.connection.commit()

class Players():
    """
    Object of all players with indexing abilites
    """
    def __init__(self, connection):
        self.connection = connection

    def addPlayer(self, name, identities=None):
        """
        Create a Player. (This makes creating Player objects in other modules
        unnecessary.
        :param name: Player name
        :type name: String
        :param identities: Identities of the new Player
        :type identities: dict
        """
        cursor = self.connection.cursor()
        Player(name, cursor, identities)

    def __getitem__(self, key):
        """
        Get Player by name
        :param key: Player name
        :type key: String
        :rtype: Player
        """
        cursor = self.conection.cursor()
        p = Player(key, cursor)
        return p

