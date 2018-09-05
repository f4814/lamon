from abc import ABC, abstractmethod

class Game(ABC):
    """ Abstract Game interface """
    def __init__(self, config):
        self.ip = config['ip']
        self.port = config['port']
        self.name = ""
        self.scores = {}
        self.config = config

        super().__init__()

    @abstractmethod
    def connect(self):
        """ Connect to the server """
        pass

    @abstractmethod
    def getPlayerScores(self):
        """
        Get player scores from the server into self.scores
        :returns: New Scores
        :rtype: Player->Score dict
        """
        pass

    def updatePlayerScores(self, players):
        """
        Update scores of the players
        :param players: List of Player objects to update
        """
        oldScores = self.scores
        newScores = self.getPlayerScores()

        for p in players:
            nick = p.getName(self.name)

            if not nick in newScores: # Player not in game
                continue
            # TODO Better round restart detection
            elif newScores[nick] == 0 and oldScores.get(nick, 0) != 0:
                continue

            gained = newScores.get(nick) - oldScores.get(nick, 0)

            if gained != 0:
                p.addScore(gained, self.name)

    @abstractmethod
    def close(self):
        """ Close the connection to the API """
        pass
