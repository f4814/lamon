from lamon import db

from sqlalchemy.orm.exc import NoResultFound

from .. import BaseTestCase
from .fake import FakeWatcher

class ManagerTestCase(BaseTestCase):
    """ Special TestCase for testing the WatcherManager """

    def tearDown(self):
        try:
            self.app.watcher_manager.stop(model=self.watcher_model)
        except ValueError:
            pass

class TestManager(ManagerTestCase):
    """ Test Watcher management """

    def test_is_running(self):
        """ Test is_running mechanism """
        self.assertFalse(self.app.watcher_manager.is_running(
            id=self.watcher_model.id))
        self.assertFalse(self.app.watcher_manager.is_running(
            model=self.watcher_model))

        self.app.watcher_manager.start(model=self.watcher_model)
        self.assertTrue(self.app.watcher_manager.is_running(
            id=self.watcher_model.id))
        self.assertTrue(self.app.watcher_manager.is_running(
            model=self.watcher_model))

        self.app.watcher_manager.stop(model=self.watcher_model)
        self.assertFalse(self.app.watcher_manager.is_running(
            id=self.watcher_model.id))
        self.assertFalse(self.app.watcher_manager.is_running(
            model=self.watcher_model))


class TestManagerStart(ManagerTestCase):
    """ Test Watcher startup """

    def test_start_id(self):
        """ Test regular starting """
        self.app.watcher_manager.start(id=self.watcher_model.id)
        self.assertTrue(self.app.watcher_manager.is_running(
            id=self.watcher_model.id))

    def test_already_running(self):
        """ Test starting already running watcher """
        with self.assertRaises(ValueError):
            self.app.watcher_manager.start(id=self.watcher_model.id)
            self.app.watcher_manager.start(id=self.watcher_model.id)

    def test_nonexistent(self):
        """ Test starting a watcher not present in the database """
        with self.assertRaises(NoResultFound):
            self.app.watcher_manager.start(id=self.watcher_model.id+1)


class TestManagerStop(ManagerTestCase):
    """ Test Watcher shutdown """

    def test_stop(self):
        """ Test regular stop """
        self.app.watcher_manager.start(id=self.watcher_model.id)
        self.app.watcher_manager.stop(id=self.watcher_model.id)
        self.assertFalse(self.app.watcher_manager.is_running(
            id=self.watcher_model.id))

    def test_already_stopped(self):
        """ Test stopping an not running watcher """
        with self.assertRaises(ValueError):
            self.app.watcher_manager.stop(id=self.watcher_model.id)

    def test_nonexistent(self):
        """ Test stopping watcher no present in the database """
        with self.assertRaises(NoResultFound):
            self.app.watcher_manager.stop(id=self.watcher_model.id+1)

class TestManagerReload(ManagerTestCase):
    """ Test Watcher reload """
