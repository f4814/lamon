from . import game
from valve.source.a2s import ServerQuerier

class ttt(game.Game):
    """ TTT (trouble in terrorist town) interface """
    def __init__(self, config):
        super().__init__(config)
        self.name = "ttt"

    def connect(self):
        """ Initialize ServerQuerier """
        self.querier = ServerQuerier((self.ip, self.port))

        # Is the correct game running?
        if self.querier.info()['game'] != 'Trouble in Terrorist Town':
            msg = 'Server (' + self.ip + ') is not running a TTT server'
            raise SourceError(msg)

    def getPlayerScores(self):
        players = self.querier.players()['players']
        self.scores = {}

        for p in players:
            self.scores[p['name']] = p['score']

        return self.scores

    def close(self):
        """ Close ServerQuerier """
        self.querier.close()


class SourceError(Exception):
    pass
