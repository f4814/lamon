import socket
import re
import time

from .. import Watcher, WatcherException
from lamon.models import Event, EventType


class Quake3Watcher(Watcher):
    """ Watcher implementing communication to Quake 3 """

    config_keys = {'address': {'type': str, 'required': True},
                   'port': {'type': int, 'required': True},
                   'timeout': {'type': int, 'required': True},
                   'rcon_password': {'type': str, 'required': True}}

    log_parser = {
        '.*Kill:.*: (.*) killed (.*) by .*': lambda e: self.die_event(e[1])
    }

    def __init__(self, **kwargs):
        super().__init__(__name__, **kwargs)

        self.connection_lost = False

    def runner(self):
        quake3 = Quake3((self.config['address'], self.config['port']),
                        self.config['timeout'], self.config['rcon_password'])

        while getattr(self, 'shutdown', True):
            try:
                info = quake3.get_info()
            except WatcherException:
                if not self.connection_lost:  # Prevent duplicate events
                    self.connection_lost_event()
                    self.connection_lost = True

                time.sleep(3)
                continue

            for key, value in info['players'].items():
                try:
                    self.score_event(self, key, value['frags'])
                except ValueError:
                    pass

            if self.connection_lost:
                self.connection_reaquired_event()
                self.connection_lost = False
            time.sleep(3)

    def _get_event_time(self, gametime):
        pass


class Quake3():
    """ Implementation of the quake3 protocol """

    def __init__(self, addr, timeout, password):
        self.packet_prefix = ('\xff' * 4).encode()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.sock.connect(addr)

        self.password = password

        # Regexes. Save here so we don't compile them everytime
        self.user_re = re.compile('\s*(\d*)\s*(\d*)\s*(\d*)\s*([^\x12]*)')
        self.map_re = re.compile('map: (.*)')

    def get_info(self):
        """ Get Server information

        :returns: Dict of server info
        :rtype: dict
        """
        result = {'players': {}}

        rcon_status = self.rcon('status')[1].replace('^7', '\x12').split('\n')

        for i in rcon_status[3:]:
            match = self.user_re.match(i)
            if match and match.group(4) is not '':
                result['players'][match.group(4)] = {
                    'frags': match.group(2),
                    'ping': match.group(3)
                }

        match = self.map_re.match(rcon_status[0])
        if match:
            result['map'] = match.group(1)

        return result

    def cmd(self, cmd):
        """ Execute a command on the server

        :type cmd: str
        :param cmd: Command to execute

        :returns: responseType, responseBody
        :rtype: tuple

        :raises: WatcherException
        """
        self.sock.send(b'\xFF\xFF\xFF\xFF' + cmd.encode())

        try:
            resp = self.sock.recv(4096)
        except (socket.timeout, socket.error) as e:
            raise WatcherException("Watcher connection failure")

        resp = resp[len(b'\xFF\xFF\xFF\xFF'):].decode().split('\n')

        responseType = resp[0]
        responseBody = '\n'.join(resp[1:])

        return responseType, responseBody

    def rcon(self, cmd):
        """ Execute a rcon command

        :type cmd: str
        :param cmd: RCON command to execute

        :returns: responseType, responseBody
        :rtype: tuple

        :raises WatcherException: Bas RCON Password
        """
        respType, respBody = self.cmd(
            f'rcon "{self.password}" {cmd}')

        if respBody == 'Bad rconpassword.\n':
            raise WatcherException("Bad RCON Password")
        elif respBody == 'No rconpassword set on the server.\n':
            raise WatcherException("No RCON Password set on the server")

        return respType, respBody

    def __del__(self):
        self.sock.close()
