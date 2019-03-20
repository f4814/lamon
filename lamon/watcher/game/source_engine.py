from valve.source.a2s import ServerQuerier, NoResponseError

from . import GameWatcher
from .. import WatcherException


class SourceEngineWatcher(GameWatcher):
    def __init__(self, model):
        configKeys = ["address", "port", "timeout", "app_id"]
        super().__init__(model, __name__, configKeys)

    def runner(self):
        # Setup valve server querier
        addr = (self.config['address'], self.config['port'])
        with ServerQuerier(addr, self.config['timeout']) as server:
            while getattr(self, 'shutdown', True):
                try:
                    if server.info()['app_id'] != int(self.config['app_id']):
                        raise WatcherException("Wrong app id on server: {}".format(server.info()['app_id']))
                    self._updatePlayers(server.players()['players'])
                except NoResponseError:
                    self.logger.warning("Watcher connection failure")

    def _updatePlayers(self, players):
        for p in players:
            if not p['name']:  # Valve doc mentions possible empty players
                continue

            self.addScore(p['name'], p['score'])

    def reload(self):
        super().reload()
        self.config['port'] = int(self.config['port'])
        self.config['timeout'] = float(self.config['timeout'])
