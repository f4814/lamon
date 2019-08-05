from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

import pytest
import os

from lamon import db
from lamon.models import WatcherConfig
from lamon.watcher.log_mixin import LogMixin
from lamon.watcher.plugin.source_engine import SourceEngineWatcher, TTTWatcher

from tests import watcher_model, session, flask


@pytest.fixture
def source_engine_watcher(watcher_model, session, monkeypatch):
    watcher_model.threadClass = 'lamon.watcher.plugin.source_engine.SourceEngineWatcher'

    watcher_model.config.append(
        WatcherConfig(key='address', value='localhost'))
    watcher_model.config.append(WatcherConfig(key='port', value='12345'))
    watcher_model.config.append(WatcherConfig(key='timeout', value='3'))
    watcher_model.config.append(WatcherConfig(key='app_id', value='3'))

    session.commit()

    watcher = SourceEngineWatcher(session=session, model_id=watcher_model.id)

    yield watcher

    try:
        watcher.stop()
    except:
        pass


@pytest.fixture
def ttt_watcher(watcher_model, session, monkeypatch):
    watcher_model.threadClass = 'lamon.watcher.plugin.source_engine.TTTWatcher'

    watcher_model.config.append(
        WatcherConfig(key='address', value='localhost'))
    watcher_model.config.append(WatcherConfig(key='port', value='12345'))
    watcher_model.config.append(WatcherConfig(key='timeout', value='3'))
    watcher_model.config.append(WatcherConfig(key='app_id', value='3'))

    session.commit()

    watcher = TTTWatcher(session=session, model_id=watcher_model.id)

    yield watcher

    try:
        watcher.stop()
    except:
        pass


class TestTTT():
    def test_join_message(self, ttt_watcher, monkeypatch):
        messages = [
            ("L 07/28/2019 - 21:51:45: \"d4rkshad0w<3><STEAM_0:1:219712654><>\" entered the game",
             "d4rkshad0w", datetime(2019, 7, 28, 21, 51, 45)),
            ("L 07/28/2019 - 21:52:09: \"pl ay er<6><STEAM_0:1:152622984><>\" entered the game",
             "pl ay er", datetime(2019, 7, 28, 21, 52, 9))
        ]

        for msg in messages:
            def mock(nick, time=None):
                assert nick == msg[1]
                assert time == msg[2]

            monkeypatch.setattr(ttt_watcher, 'join_event', mock)

            ttt_watcher.parse(msg[0])

    def test_leave_message(self, ttt_watcher, monkeypatch):
        messages = [
            ("L 07/28/2019 - 21:52:16: \"d4rkshad0w<3><STEAM_0:1:219712654><>\" disconnected (reason \"Disconnect by user.\")",
             "d4rkshad0w", datetime(2019, 7, 28, 21, 52, 16), "Disconnect by user."),
            ("L 07/28/2019 - 22:02:47: \"flohwag1<6><STEAM_0:1:152622984><>\" disconnected (reason \"Disconnect by user.\")",
             "flohwag1", datetime(2019, 7, 28, 22, 2, 47), "Disconnect by user.")
        ]

        for msg in messages:
            def mock(nick, time=None, info=None):
                assert nick == msg[1]
                assert time == msg[2]
                assert info == msg[3]

            monkeypatch.setattr(ttt_watcher, 'leave_event', mock)

            ttt_watcher.parse(msg[0])

    def test_kill_message(self, ttt_watcher, monkeypatch):
        messages = [
            ("L 07/28/2019 - 21:53:40: 00:43.100 - KILL:	 JanCS [traitor] killed ugulugu [innocent]",
             "ugulugu", datetime(2019, 7, 28, 21, 53, 40), "JanCS"),
            ("L 07/28/2019 - 21:57:00: 04:03.57 - KILL:	 JanCS [traitor] killed flohwag1 [innocent]",
             "flohwag1", datetime(2019, 7, 28, 21, 57, 0), "JanCS")
        ]

        for msg in messages:
            def mock(nick, time=None, info=None):
                assert nick == msg[1]
                assert time == msg[2]
                assert info == msg[3]

            monkeypatch.setattr(ttt_watcher, 'die_event', mock)

            ttt_watcher.parse(msg[0])
