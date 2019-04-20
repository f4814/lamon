import threading
import time

from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

from lamon.watcher import load_watcher_class, Watcher
from lamon.watcher.game.source_engine import SourceEngineWatcher
from lamon.models import Watcher as WatcherModel
from lamon.models import Event, EventType
from lamon import db

from .. import BaseTestCase
from .fake import FakeWatcher


class TestCreateObject(BaseTestCase):
    """ Test Dynamic Loading mechanism. """

    def test_create(self):
        """ Test creation of a simple watcher object (SourceEngine) """
        source_engine = load_watcher_class(
            'lamon.watcher.game.source_engine.SourceEngineWatcher')
        self.assertTrue(source_engine == SourceEngineWatcher)

    def test_create_abc(self):
        """ Test for correct error when creating abstract watcher class """
        with self.assertRaises(TypeError):
            abc_ = load_watcher_class('lamon.watcher.Watcher')
            abc_()

    def test_create_invalid(self):
        """ Test for correct error when creating a non-watcher object """
        with self.assertRaises(TypeError):
            load_watcher_class('tests.BaseTestCase')


class TestWatcher(BaseTestCase):
    """ Test watcher built in functions """

    def setUp(self):
        """ Start a fake watcher """
        super().setUp()
        session = scoped_session(sessionmaker(bind=db.engine))

        self.watcher = FakeWatcher(
            session=session, model_id=self.watcher_model.id,
            config_keys=['key1', 'key2', 'key3'])

    def tearDown(self):
        """ Kill fake watcher """
        try:
            self.watcher.stop()
        except RuntimeError:
            pass

        super().tearDown()

    def test_invalid_threadClass(self):
        """ Test for correct error when initializing watcher with wrong model """
        with self.assertRaises(TypeError):
            model = self.watcher
            model.threadClass = 'nop'

            FakeWatcher(model, [])

    def test_start(self):
        """ Test starting watcher thread """
        query = db.session.query(Event).\
            filter(Event.watcherID == self.watcher._model_id).\
            filter(Event.type == int(EventType.JOIN))
        before = len(query.all())

        self.watcher.start()
        time.sleep(1)  # Give watcher time to make db request

        after = len(query.all())
        self.assertEqual(after, before + 1)

        for t in threading.enumerate():
            if isinstance(t, Watcher):
                if t.name == self.watcher.name:
                    return

        self.assertTrue(False)  # Thread not found

    def test_stop(self):
        """ Test stopping watcher thread """
        query = db.session.query(Event).\
            filter(Event.watcherID == self.watcher._model_id).\
            filter(Event.type == int(EventType.LEAVE))

        self.watcher.start()

        before = len(query.all())
        self.watcher.stop()
        self.watcher.join()
        after = len(query.all())

        self.assertEqual(after, before + 1)

        for t in threading.enumerate():
            if isinstance(t, Watcher):
                self.assertFalse(t.name == self.watcher.name)

    def test_reload(self):
        """ Test reloading mechanism """
        query = db.session.query(Event).\
            filter(Event.watcherID == self.watcher._model_id).\
            filter(Event.type == int(EventType.RELOAD))

        self.watcher.start()
        time.sleep(1) # Wait for watcher to finish

        for i in self.watcher_model.config:
            i.value = "updated"

        db.session.commit()

        before = len(query.all())
        self.watcher.reload()
        after = len(query.all())

        self.assertEqual(after, before + 1)

        for key, value in self.watcher.config.items():
            self.assertTrue(value == "updated")

    def test_add_event(self):
        """ Test event adding """
        e = Event(type=1, time=datetime.now(), info='TEST')
        self.watcher.add_event(e)

        query = db.session.query(Event).\
            filter(Event.id == e.id)
        res = query.one()

        self.assertEqual(e.id, res.id)
        self.assertEqual(e.time, res.time)
