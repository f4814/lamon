from valve.source.a2s import ServerQuerier

from . import GameWatcher
from .. import WatcherException


class SourceEngineWatcher(GameWatcher):
    def __init__(self, model):
        print(__name__)
        super().__init__(model, __name__)
        self.load_config()
        self.server_name = ""

    def load_config(self):
        self._address = "185.82.20.194"
        self._port = 27015
        self._timeout = 2
        self._state = ""
        self._app_id = 4000

    def run(self):
        # Setup valve server querier
        with ServerQuerier((self._address, self._port), self._timeout) as server:
            if server.info()['app_id'] != self._app_id:
                raise WatcherException("Wrong app id on server")
            while getattr(self, 'shutdown', True):
                # self.server_name = server.info()['server_name']
                self._updatePlayers()

    def _updatePlayers(self):
        pass
