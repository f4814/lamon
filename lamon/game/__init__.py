import logging

from abc import ABC, abstractmethod
from time import sleep

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
        Get player scores from the server into self._scores
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

        for player, score in oldScores.items():
            if newScores.get(player, score) != score: # Update Scores
                points = newScores[player] - score
                self.players[player].addScore(points, self.name) # TODO Error

            if not player in newScores: # Check if player quit
                self.players[player].quit(self.gameName)

        for player in newScores: # Check if player entered
            if not player in oldScores:
                self.players[player].online(self.gameName)

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
                logger.error(str(e))
            sleep(self.delay)

        self.close()

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
