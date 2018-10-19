"""
Player Abstractions
"""
import sqlite3
import logging

from datetime import datetime
from dateutil import parser

logger = logging.getLogger(__name__)

class Player():
    """
    A player and set of identities on the servers
    Player objects are created by the Players object and should only be used
    for one task.
    """
    def __init__(self, name, cursor, identities=None, create=True):
        """
        :param name: Player name
        :type name: String
        :type cursor: Cursor
        :param identities: Identities to add to the Player
        :type identites: Dict
        :param create: Create user if not existent
        :type create: Bool
        :raises: PlayerNameError
        """
        self.name = name
        self._cursor = cursor

        # Add player to database if not already existent
        query = "SELECT * FROM player WHERE name=?"
        add = "INSERT INTO player VALUES(?)"

        if not cursor.execute(query, (name,)).fetchone():
            if create:
                logger.debug('Creating player ' + name)
                cursor.execute(add, (name,))
                cursor.connection.commit()
            else:
                raise PlayerNameError('Player ' + name + ' does not exist')
        elif create:
            raise PlayerNameError('Player ' + name + ' already exists')

        # Add identities
        if identities:
            self.addIdentity(identities)

    def addIdentity(self, identity):
        """
        Add a identity to the Player
        :param identity: Identity dict
        :type identity: dict
        :raises: PlayerIdentityError
        """
        add = "INSERT INTO identity VALUES (?,?,?)"
        for game, nick in identity.items():
            try:
                self.getName(game)
            except PlayerIdentityError:
                self._cursor.execute(add, (game, nick, self.name))
                logger.debug('Adding identity ' + nick + ' for game ' + game +
                            ' for player ' + self.name)
            else:
                raise PlayerIdentityError('Player ' + self.name + ' already ' +
                                          'already has an identity in ' + game)
        self._cursor.connection.commit()

    def getName(self, gameName):
        """
        Find the nickname in game
        :param gameName: Name of the Game
        :param gameName: String
        :raises: PlayerIdentityError
        """
        query = """
            SELECT nick FROM identity WHERE gameName=? AND playerName=?
        """
        self._cursor.execute(query, (gameName, self.name))
        nick = self._cursor.fetchone()
        if nick != None:
            return nick[0]
        else:
            raise PlayerIdentityError('Player ' + self.name + ' has no ' +
                                      'identity in game ' + gameName)

    def getScore(self, gameNames=None):
        """
        Get the score of a player
        :param gameNames: List of games to read the score from. None is all
        :returns: Int score
        """
        score = 0
        querySimple = "SELECT points FROM scoreUpdate WHERE playerName=?"
        queryMany = """
            SELECT points FROM scoreUpdates
                WHERE gameName REGEXP ?
                AND playerName=?
            """

        if gameNames:
            scores = self._cursor.execute(queryMany, '|'.join(gameNames),
                                         self.name)
            msg = 'in games' + ', '.join(gameNames)
        else:
            scores = self._cursor.execute(querySimple, (self.name,))
            msg = 'in all games'

        for s in scores:
            score += s

        logger.debug(self.name + '\'s score ' + msg + ' is: ' + str(score))
        return score

    def addPoints(self, points, gameName):
        """
        Add points to player.
        :param points: Int gained points
        :type points: Integer
        :param gameName: Name of the game
        :type gameName: String
        """
        query = "INSERT INTO scoreUpdate (?, ?, ?, ?)"
        logger.debug('Adding ' + str(points) + ' in game ' + gameName + ' to' +
                     self.name)
        self._cursor.execute(query, (points, str(datetime.now()),
                             gameName, self.name))
        self._cursor.connection.commit()

    def getTimeInGame(self, gameNames=None):
        """
        Get the time player has spent in games. (Default = all)
        :param gameNames: Games to get the time from
        :type gameName: List
        :rtype: Integer (seconds)
        """
        query = """
            SELECT timespan FROM inGame
            WHERE playerName=?  AND gameName REGEXP ?  AND NOT timespan=-1
        """

        if gameNames:
            result = self._cursor.execute(
                query, (self.name, '|'.join(gameNames))).fetchall()
            msg = 'in games' + ', '.join(gameNames)
        else:
            result = self._cursor.execute(query, (self.name, '.*')).fetchall()
            msg = 'in all games'

        span = 0
        for i in result:
            span += i[0]

        logger.debug(self.name + 'has spent ' + str(span) + 's ' + msg)
        return span

    def enter(self, gameName, time=datetime.now()):
        """
        Player enters a game. Initial row in the db is created:
        :param gameName: gameName
        :type gameName: string
        :param time: The time to use instead of datetime.now()
        :type time: datetime
        :raises: PlayerStateError
        """
        query = "SELECT * FROM inGame WHERE playerName=? AND gameName=?"
        add = "INSERT INTO inGame VALUES (?,?,?,-1)"

        if not self._cursor.execute(query, (self.name, gameName)).fetchone():
            self._cursor.execute(add, (self.name, gameName, str(time)))
            logger.debug(self.name + ' enters ' + gameName)
        else:
            raise PlayerStateError("Player can not enter game")

    def quit(self, gameName, now=datetime.now()):
        """
        Player leaves a game. The timespan in the db is set.
        :param gameName: gameName
        :type gameName: string
        :param now: The time to use instead of datetime.now()
        :type now: datetime
        :raises: PlayerStateError
        """
        query = """
            SELECT time
            FROM inGame
            WHERE playerName=? AND gameName=? AND timespan=-1
        """

        update = """
            UPDATE inGame
            SET timespan=?
            WHERE playerName=? AND gameName=? AND timespan=-1
        """

        time = self._cursor.execute(query, (self.name, gameName)).fetchone()
        if time:
            delta = now - parser.parse(time[0])
            newTimespan = delta.total_seconds()
            self._cursor.execute(update, (newTimespan, self.name, gameName))
            self._cursor.connection.commit()
            logger.debug(self.name + ' quits ' + gameName)
        else:
            raise PlayerStateError("Player can not quit game")


class Players():
    """
    Object of all players with indexing abilites
    """
    def __init__(self, sqlConn):
        self._sqlConn = sqlConn

    def addPlayer(self, name, identities=None):
        """
        Create a Player. (This makes creating Player objects in other modules
        unnecessary.
        :param name: Player name
        :type name: String
        :param identities: Identities of the new Player
        :type identities: dict
        :raises: PlayerNameError
        """
        cursor = self._sqlConn.cursor()
        Player(name, cursor, identities, create=True)

    def getPlayer(self, name):
        """ Name for __getitem__"""
        return self[name]

    def __getitem__(self, key):
        """
        Get Player by name
        :param key: Player name
        :type key: String
        :rtype: Player
        :raises: PlayerNameError
        """
        cursor = self._sqlConn.cursor()
        p = Player(key, cursor, create=False)
        return p

class PlayerError(Exception):
    pass

class PlayerNameError(PlayerError):
    pass

class PlayerIdentityError(PlayerError):
    pass

class PlayerStateError(PlayerError):
    pass
