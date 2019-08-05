from unittest.mock import MagicMock

import pytest

from sqlalchemy.orm import scoped_session, sessionmaker

from lamon import db
from lamon.models import WatcherConfig
from lamon.watcher.plugin.quake3 import Quake3Watcher, Quake3
from lamon.watcher import WatcherException

from tests import watcher_model, session, flask


# @pytest.fixture
# def quake3_watcher(watcher_model, session, monkeypatch):
#     """ Set up a quake3 watcher with a mock socket """
#     watcher_model.threadClass = 'lamon.watcher.plugin.quake3.Quake3Watcher'
#     session.commit()
#
#     watcher_model.config.append(
#         WatcherConfig(key='address', value='localhost'))
#     watcher_model.config.append(
#         WatcherConfig(key='port', value='12345'))
#     watcher_model.config.append(
#         WatcherConfig(key='timeout', value='3'))
#     watcher_model.config.append(
#         WatcherConfig(key='rcon_password', value='secret'))
#
#     session.commit()
#
#     session = scoped_session(sessionmaker(bind=db.engine))
#
#     mock_socket = MagicMock()
#
#     watcher = Quake3Watcher(
#         session=session, model_id=watcher_model.id)
#     watcher.sock.close()
#     watcher.sock = mock_socket
#
#     yield watcher
#
#     try:
#         watcher.stop()
#     except RuntimeError:
#         pass


@pytest.fixture
def quake3():
    """ Set up a mock Quake3 object """
    q = Quake3(('localhost', 5000), 1, '1234')
    q.sock.close()
    q.sock = MagicMock()

    return q

class TestQuake3():
    """ Test the Quake3 Watcher """

    def test_cmd(self, quake3):
        """ Test correct command sending / receiving """
        quake3.sock.recv.return_value = b'\xFF\xFF\xFF\xFFprint\nte\nst'
        resp = quake3.cmd('test')

        quake3.sock.send.assert_called_with(
            b'\xFF\xFF\xFF\xFF' + b'test')

        assert resp == ('print', 'te\nst')

    def test_badPassword(self, quake3):
        """ Test for correct exception on bad password """
        quake3.sock.recv.return_value = b'\xff\xff\xff\xffprint\nBad rconpassword.\n'

        with pytest.raises(WatcherException):
            quake3.get_info()

    def test_get_info(self, quake3, monkeypatch):
        """ Test parsing of the status string """
        def mock(*args):
            return ('print', 'map: Q3 DM1\nnum score ping name            lastmsg address               qport rate\n--- ----- ---- --------------- ------- --------------------- ----- -----\n  0     0    0 Unnamed Player^7         0 l oopback              33978 99999\n  1     0  999 Angel^7                 0 bot                       0 16384\n  2     0  999 Angel^7                 0 bot                       0 16384\n  3     0  999 Cadavre^7  0 bot                       0 16384\n  4     0  999 Cadavre^7               0 bot                       0 16384\n  5     0  999 Bitterman^7             0 bot                       0 16384\n  6     0 999 Bitterman^7             0 bot                       0 16384\n  7     0  999 Crash^7                 0 bot                       0 16384\n\n')

        quake3.rcon = mock
        info = quake3.get_info()

        assert info['players'] == {
            'Unnamed Player': {
                'frags': '0',
                'ping': '0'
            },
            'Angel': {
                'frags': '0',
                'ping': '999'
            },
            'Cadavre': {
                'frags': '0',
                'ping': '999'
            }, 'Bitterman': {
                'frags': '0',
                'ping': '999'
            },
            'Crash': {
                'frags': '0',
                'ping': '999'
            }
        }
        assert info['map'] == 'Q3 DM1'
