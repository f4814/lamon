import threading

from lamon.watcher import load_watcher_class, Watcher
from lamon.watcher.game.source_engine import SourceEngineWatcher
from lamon.models import Watcher as WatcherModel
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
        self.watcher = FakeWatcher(self.watcher_model, [])

    def tearDown(self):
        """ Kill fake watcher """
        try:
            self.watcher.stop()
        except RuntimeError:
            pass

        super().tearDown()

    def test_start(self):
        """ Test starting watcher thread """
        self.watcher.start()
        self.assertTrue(self.watcher._model.state == 'RUNNING')

        # Check database sync of watcher Model
        watcher_id = self.watcher._model.id
        query = db.session.query(WatcherModel).filter(WatcherModel.id == watcher_id)
        self.assertTrue(query.one().state == 'RUNNING')

        for t in threading.enumerate():
            if isinstance(t, Watcher):
                if t.name == self.watcher.name:
                    return

        self.assertTrue(False)

    def test_stop(self):
        """ Test stopping watcher thread """
        self.watcher.start()
        self.watcher.stop()
        self.watcher.join()

        for t in threading.enumerate():
            if isinstance(t, Watcher):
                self.assertFalse(t.name == self.watcher.name)

        self.assertTrue(self.watcher._model.state == 'STOPPED')

        # Check database sync of watcher Model
        watcher_id = self.watcher._model.id
        query = db.session.query(WatcherModel).filter(WatcherModel.id == watcher_id)
        self.assertTrue(query.one().state == 'STOPPED')

    def test_reload(self):
        """ Test reloading mechanism """

    def test_add_score(self):
        """ Test score adding """
