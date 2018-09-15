from abc import abstractmethod
from valve.source.a2s import ServerQuerier, NoResponseError

from lamon.game import Game, GameConnectionError, GameTypeError

class Source(Game):
    """ Generic interface to games using the source engine """
    @abstractmethod
    def __init__(self, players, config):
        super().__init__(players, config)

    def connect(self):
        """ Initialize ServerQuerier """
        self.querier = ServerQuerier((self.ip, self.port))

        # Is the correct game running?
        try:
            if self.querier.info()['game'] != self.internalName:
                msg = 'Server (' + self.ip + ') is not running the specified game'
                raise GameTypeError(self.name, msg)
        except NoResponseError:
            raise GameConnectionError(self.name, (self.ip, self.port),
                                     'Cannot connect to server')

    def getPlayerScores(self):
        self.scores = {}

        try:
            players = self.querier.players()['players']
        except NoResponseError:
            raise GameConnectionError(self.name, (self.ip, self.port),
                                     'Cannot connect to server')

        for p in players:
            self.scores[p['name']] = p['score']

        return self.scores

    def close(self):
        """ Close ServerQuerier """
        self.querier.close()
