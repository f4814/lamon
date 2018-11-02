import logging

from abc import ABC, abstractmethod
from time import sleep

from lamon.player import Player, PlayerNickError, PlayerStateError

logger = logging.getLogger(__name__)

class Game(ABC):
    """
    Abstract Game interface
    :member ip: server ip
    :memper port: server port
    :member delay: time to wait between polls
    :member name: name of the game
    :member scores: old scores
    :member config: server config
    :member hasTemplate: Does the game provide a template? Default: False
    :mameber players: Global players object
    """
    def __init__(self, players, config):
        self.ip = config['ip']
        self.port = config['port']
        self.delay = config['delay']
        self.timeout = config.get('timeout', 10)
        self.name = ""
        self._scores = {}
        self._config = config
        self.hasTemplate = False
        self.players = players

        super().__init__()

    @abstractmethod
    def connect(self):
        """ Connect to the server """
        pass

    @abstractmethod
    def getPlayerScores(self):
        """
        Return scores from server (nick->scores dict)
        Has to return a score for EVERY PLAYER on the server, otherwise
        self.updatePlayers has to be overwritten.
        :returns: New Scores
        :rtype: Player->Score dict
        """
        pass

    def updatePlayers(self):
        """
        Update scores of the players and mark them as online
        """
        oldScores = self._scores
        newScores = self.getPlayerScores()

        for nick, score in oldScores.items():
            if newScores.get(nick, score) != score: # Update Scores
                points = newScores[nick] - score
                logger.debug('Nick ' + nick + ' earned ' + str(points) +
                             ' in ' + self.name)
                self._safePlayer(nick, Player.addPoints, (points, self.name))

            if not nick in newScores: # Check if player quit
                logger.debug('Nick ' + nick + ' left ' + self.name)
                self._safePlayer(nick, Player.quit, (self.name,))

        for nick in newScores: # Check if player entered
            if not nick in oldScores:
                logger.debug('Nick ' + nick + ' entered ' + self.name)
                self._safePlayer(nick, Player.enter, (self.name,))

        self._scores = newScores

    def dispatch(self):
        """
        Keep the game object and player object as up-to-date as possible. This
        is started in a new thread by the core. Exceptions are ignored.

        If the game provides some sort of streaming API, this can be
        overwritten.
        """
        try:
            self.connect()
        except GameConnectionError:
            pass

        while True:
            try:
                self.updatePlayers()
            except GameConnectionError as e:
                logger.warn(str(e))
            sleep(self.delay)

        self.close()

    def _safePlayer(self, nick, method, args=()):
        """
        Call a method of the Player object and handle errors
        """
        try:
            method(self.players.getByNick(self.name, nick), *args)
        except PlayerNickError as e:
            logger.warn(e.message)
        except PlayerStateError as e:
            logger.warn(e.message)

    @abstractmethod
    def close(self):
        """ Close the connection to the API """
        pass


class GameError(Exception):
    def __init__(self, game, address, message):
        super().__init__('[' + game + '] ' + str(address) + ' ' + message)

class GameTypeError(GameError):
    pass

class GameConnectionError(GameError):
    pass
