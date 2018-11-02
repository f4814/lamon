import logging

from abc import abstractmethod
from valve.source.a2s import ServerQuerier, NoResponseError

from . import Game, GameConnectionError, GameTypeError

logger = logging.getLogger(__name__)

class Source(Game):
    """ Generic interface to games using the source engine """
    @abstractmethod
    def __init__(self, players, config):
        super().__init__(players, config)

    def connect(self):
        """ Initialize ServerQuerier """
        self.querier = ServerQuerier((self.ip, self.port), self.timeout)

        # Is the correct game running?
        try:
            if self.querier.info()['game'] != self.internalName:
                msg = 'Server (' + self.ip + ') is not running the specified game'
                raise GameTypeError(self.name, self.ip, msg)
        except NoResponseError:
            raise GameConnectionError(self.name, (self.ip, self.port),
                                     'Cannot connect to server')

        logger.info('Connected to ' + self.name + ' server on ' +
                    str((self.ip, self.port)) + '.')

    def getPlayerScores(self):
        scores = {}

        try:
            players = self.querier.players()['players']
        except NoResponseError:
            raise GameConnectionError(self.name, (self.ip, self.port),
                                     'Cannot connect to server')

        for p in players:
            scores[p['name']] = p['score']

        logger.debug(scores)
        return scores

    def close(self):
        """ Close ServerQuerier """
        logger.info('Closing connection to ' + self.name + 'server on ' +
                    str((self.ip, self.port)))
        self.querier.close()
