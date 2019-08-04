import threading
import time

import pytest

from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

from lamon.watcher import load_watcher_class, Watcher
from lamon.watcher.plugin.source_engine import SourceEngineWatcher
from lamon.models import Watcher as WatcherModel
from lamon.models import Event, EventType

from .. import fake_watcher, session, flask, watcher_model
from . import FakeWatcher


class TestCreateObject():
    """ Test Dynamic Loading mechanism. """

    def test_create(self):
        """ Test creation of a simple watcher object (SourceEngine) """
        source_engine = load_watcher_class(
            'lamon.watcher.plugin.source_engine.SourceEngineWatcher')
        assert source_engine == SourceEngineWatcher

    def test_create_abc(self):
        """ Test for correct error when creating abstract watcher class """
        with pytest.raises(TypeError):
            abc_ = load_watcher_class('lamon.watcher.Watcher')
            abc_()

    def test_create_invalid(self):
        """ Test for correct error when creating a non-watcher object """
        with pytest.raises(TypeError):
            load_watcher_class('datetime.datetime')


class TestWatcher():
    """ Test watcher built in functions """

    def test_invalid_threadClass(self, fake_watcher):
        """ Test for correct error when initializing watcher with wrong model """
        with pytest.raises(TypeError):
            model, _ = fake_watcher
            model.threadClass = 'nop'

            FakeWatcher(model, [])

    def test_start(self, fake_watcher, session):
        """ Test starting watcher thread """
        query = session.query(Event).\
            filter(Event.watcherID == fake_watcher._model_id).\
            filter(Event.type == int(EventType.WATCHER_START))
        before = len(query.all())

        fake_watcher.start()
        time.sleep(1)  # Give watcher time to make db request

        after = len(query.all())
        assert after == before + 1

        for t in threading.enumerate():
            if isinstance(t, Watcher):
                if t.name == fake_watcher.name:
                    return

        assert False  # Thread not found

    def test_stop(self, fake_watcher, session):
        """ Test stopping watcher thread """
        query = session.query(Event).\
            filter(Event.watcherID == fake_watcher._model_id).\
            filter(Event.type == int(EventType.WATCHER_STOP))

        fake_watcher.start()

        before = len(query.all())
        fake_watcher.stop()
        fake_watcher.join()
        after = len(query.all())

        assert after == before + 1

        for t in threading.enumerate():
            if isinstance(t, Watcher):
                assert t.name != fake_watcher.name

    def test_missing_keys(self, monkeypatch, watcher_model, session):
        """ Test watcher reacting to missing, required config-keys """
        with pytest.raises(KeyError):
            print(FakeWatcher.config_keys)
            fake_watcher = FakeWatcher(session=session, model_id=watcher_model.id,
                                       config_keys={'missing': {'required': True, 'type': str}})


class TestWatcherEvents():
    def test_add_event(self, fake_watcher, session):
        """ Test event adding """
        e = Event(type=EventType.WATCHER_START,
                  time=datetime.now(), info='TEST')
        fake_watcher._add_event(e)

        query = session.query(Event).\
            filter(Event.id == e.id)
        res = query.one()

        assert e.id == res.id
        assert e.time == res.time
