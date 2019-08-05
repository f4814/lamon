from valve.source.a2s import ServerQuerier, NoResponseError
from socket import gaierror
from time import sleep
from datetime import datetime

from .. import Watcher, WatcherException
from ..log_mixin import LogMixin
from lamon.models import EventType


class SourceEngineWatcher(Watcher):
    """
    Watcher implementating communication to games based on Valve's source
    engine
    """

    config_keys = {'address': {'type': str, 'required': True},
                   'port': {'type': int, 'required': True},
                   'timeout': {'type': int, 'required': True},
                   'app_id': {'type': int, 'required': True,
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
        server_info = None

        with ServerQuerier(addr, self.config['timeout']) as server:
            while getattr(self, 'shutdown', True):
                try:
                    server_info = server.info()
                except (NoResponseError, gaierror):
                    self.connection_lost_event()
                    sleep(self.config['timeout'])
                    continue

                if server_info['app_id'] != int(self.config['app_id']):
                    raise WatcherException(f'Wrong app id on server: {server_info["app_id"]}')
                self._updatePlayers(server.players()['players'])

                self.connection_reaquired_event()

    def _updatePlayers(self, players):
        for p in players:
            if not p['name']:  # Valve doc mentions possible empty players
                continue

            self.score_event(p['name'], p['score'])


class TTTWatcher(SourceEngineWatcher, LogMixin):
    """ Like a SourceEngineWatcher. But is able to parse TTT logfiles """
    log_header_short = '^L (\d\d\/\d\d\/\d{4} - \d\d:\d\d:\d\d): '
    log_header_long = log_header_short + '\d\d:\d\d.\d\d - '

    log_kill_message = log_header_long + 'KILL:\s*(.*) \[.*\] killed (.*) \[.*\]$'
    log_join_message = log_header_short + '"(.*)<\d*><STEAM_.*><>" entered the game'
    log_leave_message = log_header_short + '"(.*)<\d*><STEAM_.*><>" disconnected \(reason "(.*)"\)'
    def __init__(self, *args, **kwargs):
        self.log_parser = {
            self.log_kill_message: lambda e: self._log_message(e, EventType.USER_DIE),
            self.log_join_message: lambda e: self._log_message(e, EventType.USER_JOIN),
            self.log_leave_message: lambda e: self._log_message(e, EventType.USER_LEAVE)
        }

        super().__init__(*args, **kwargs)

    def _log_message(self, expr, type):
        time = datetime.strptime(expr[1], '%m/%d/%Y - %H:%M:%S')

        if type is EventType.USER_DIE:
            self.die_event(expr[3], time=time, info=expr[2])
        elif type is EventType.USER_JOIN:
            self.join_event(expr[2], time=time)
        elif type is EventType.USER_LEAVE:
            self.leave_event(expr[2], time=time, info=expr[3])
