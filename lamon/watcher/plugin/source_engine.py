from valve.source.a2s import ServerQuerier, NoResponseError

from .. import Watcher, WatcherException
from lamon.models import Event, EventType


class SourceEngineWatcher(Watcher):
    """Watcher implementating communication to games based on Valve's source
    engine
    """

    config_keys = {'address': {'type': 'str', 'required': True},
                   'port': {'type': int, 'required': True},
                   'timeout': {'type': int, 'required': True},
                   'app_id:': {'type': int, 'required': True,
                               'hint':
                               """this is the app ID of the client, not the
                               server. For example, for Team Fortress 2 440 has
                               to be used instead of 232250 which is the ID of
                               the server software."""}}

    def __init__(self, **kwargs):
        super().__init__(__name__, **kwargs)

    def runner(self):
        # Setup valve server querier
        addr = (self.config['address'], self.config['port'])
        connection_lost = False
        server_info = None

        with ServerQuerier(addr, self.config['timeout']) as server:
            while getattr(self, 'shutdown', True):
                try:
                    server_info = server.info()
                except NoResponseError:
                    self.add_event(
                        Event(type=EventType.WATCHER_CONNECTION_LOST))
                    self.logger.debug("Watcher connection failure")
                    connection_lost = True
                    continue

                if server_info['app_id'] != int(self.config['app_id']):
                    raise WatcherException(
                        "Wrong app id on server: {}".format(server_info['app_id']))
                self._updatePlayers(server.players()['players'])

                if connection_lost:  # Watcher reaquired connection
                    self.add_event(
                        Event(type=EventType.WATCHER_CONNECTION_REAQUIRED))

    def _updatePlayers(self, players):
        for p in players:
            if not p['name']:  # Valve doc mentions possible empty players
                continue

            self.add_score(p['name'], p['score'])
