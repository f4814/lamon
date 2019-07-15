from unittest.mock import MagicMock

import pytest

from sqlalchemy.orm import scoped_session, sessionmaker

from lamon import db
from lamon.models import WatcherConfig
from lamon.watcher.plugin.quake3 import Quake3Watcher

from tests import watcher_model, session, flask


@pytest.fixture
def quake3_watcher(watcher_model, session, monkeypatch):
    """ Set up a quake3 watcher with a mock socket """
    watcher_model.threadClass = 'lamon.watcher.plugin.quake3.Quake3Watcher'
    session.commit()

    watcher_model.config.append(
        WatcherConfig(key='address', value='localhost'))
    watcher_model.config.append(
        WatcherConfig(key='port', value='12345'))
    watcher_model.config.append(
        WatcherConfig(key='timeout', value='3'))
    watcher_model.config.append(
        WatcherConfig(key='rcon_password', value='secret'))

    session.commit()

    session = scoped_session(sessionmaker(bind=db.engine))

    mock_socket = MagicMock()

    watcher = Quake3Watcher(
        session=session, model_id=watcher_model.id)
    watcher.sock.close()
    watcher.sock = mock_socket

    yield watcher

    try:
        watcher.stop()
    except RuntimeError:
        pass


class TestQuake3():
    """ Test the Quake3 Watcher """

    def test_connect(self, quake3_watcher):
        """ Test connecting and emmiting of correct events """
        quake3_watcher.start()
        quake3_watcher.stop()

        quake3_watcher.sock.connect.assert_called_with(
            (quake3_watcher.config['address'], int(quake3_watcher.config['port'])))

    def test_cmd(self, quake3_watcher):
        """ Test correct command sending / receiving """
        quake3_watcher.sock.recv.return_value = b'\xFF\xFF\xFF\xFFprint\nte\nst'
        resp = quake3_watcher.cmd('test')

        quake3_watcher.sock.send.assert_called_with(
            b'\xFF\xFF\xFF\xFF' + b'test')

        assert resp == ('print', 'te\nst')

    def test_badPassword(self, quake3_watcher):
        """ Test for correct exception on bad password """

    def test_get_info(self, quake3_watcher):
        """ Test parsing of the status string """
