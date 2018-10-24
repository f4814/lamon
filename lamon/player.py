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
    A player and set of nicknames on the servers
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
                raise PlayerNameError(name, 'Player does not exist')
        elif create:
            raise PlayerNameError(name, 'Player already exists')

        # Add identities
        if identities:
            self.addNick(identities)

    def addNick(self, nick):
        """
        Add a nick to the Player
        :param nick: Dict of gameNames (key) and nickNames (values)
        :type nick: dict
        :raises: PlayerNickError
        """
        add = "INSERT INTO nick VALUES (?,?,?)"
        for game, nick in nick.items():
            try:
                self.getNick(game)
            except PlayerNickError:
                self._cursor.execute(add, (game, nick, self.name))
                logger.debug('Adding nick ' + nick + ' for game ' + game +
                            ' for player ' + self.name)
            else:
                raise PlayerNickError(self.name, 'Player already ' +
                                      'has a nick in ' + game)
        self._cursor.connection.commit()

    def hasNick(self, gameName):
        """
        Check wether the player has a nickname in game
        :param gameName: game Name
        :type gameName: str
        :rtype: Bool
        """
        query = "SELECT nick FROM nick WHERE playerName=? AND gameName=?"
        result = self._cursor.execute(query, (self.name, gameName)).fetchone()
        if result != None:
            return True
        else:
            logger.debug(self.name + ' has no nick in ' + gameName)
            return False

    def getNick(self, gameName):
        """
        Find the nickname in game
        :param gameName: Name of the Game
        :param gameName: String
        :raises: PlayerNickError
        """
        query = """
            SELECT nick FROM nick WHERE gameName=? AND playerName=?
        """
        self._cursor.execute(query, (gameName, self.name))
        nick = self._cursor.fetchone()
        if nick != None:
            return nick[0]
        else:
            raise PlayerNickError(self.name, 'Player has no ' +
                                  'nick in game ' + gameName)

    def getScore(self, gameNames=None):
        """
        Get the score of a player
        :param gameNames: List of games to read the score from. None is all
        :type gameName: List
        :returns: Int score
        """
        score = 0
        query = """
            SELECT points FROM scoreUpdate
            WHERE playerName=? AND gameName REGEXP ?
        """

        if gameNames:
            scores = self._cursor.execute(
                query, (self.name, '|'.join(gameNames))).fetchall()
            msg = 'in games ' + ', '.join(gameNames)
        else:
            scores = self._cursor.execute(query, (self.name, '.*')).fetchall()
            msg = 'in all games'

        for s in scores:
            score += s[0]

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
        query = "INSERT INTO scoreUpdate VALUES (?, ?, ?, ?)"
        logger.debug('Adding ' + str(points) + ' points in game ' + gameName + ' to' +
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

    def inGame(self, gameName):
        """
        Check if player is ingame
        :param gameName: gameName
        :type gameName: str
        :rtype: Bool
        """
        query = """
            SELECT * FROM inGame
            WHERE playerName=? AND gameName=? AND timespan=-1
        """
        result = self._cursor.execute(query, (self.name, gameName)).fetchone()
        return result != None

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
            logger.debug(self.name + ' entered ' + gameName)
        else:
            raise PlayerStateError(self.name, "Player can not enter game")

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
            logger.debug(self.name + ' quit ' + gameName)
        else:
            raise PlayerStateError(self.name, "Player can not quit game")


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

    def getByNick(self, gameName, nick):
        """
        Get a player by his nickname in game
        :rtype: Player:
        :raises: PlayerNickError
        """
        cursor = self._sqlConn.cursor()
        query = "SELECT playerName FROM nick WHERE nick=? AND gameName=?"
        result = cursor.execute(query, (nick, gameName)).fetchone()

        if result != None:
            return Player(result[0], cursor, create=False)
        else:
            raise PlayerNickError("None", 'No nick ' + nick + ' in game ' + gameName)

    def __getitem__(self, key):
        """
        Get Player by name
        :param key: Player name
        :type key: String
        :rtype: Player
        :raises: PlayerNameError
        """
        cursor = self._sqlConn.cursor()

        if type(key) == str:
            return Player(key, cursor, create=False)
        elif type(key) == int:
            query = "SELECT name FROM player"
            result = cursor.execute(query).fetchall()[key][0]
            return Player(result, cursor, create=False)


class PlayerError(Exception):
    def __init__(self, playerName, msg):
        self.playerName = playerName
        self.msg = msg
        self.message = '[' + playerName + ']' + ' ' + msg

        super().__init__(self.message)

class PlayerNameError(PlayerError, IndexError):
    pass

class PlayerNickError(PlayerError):
    pass

class PlayerStateError(PlayerError):
    pass
