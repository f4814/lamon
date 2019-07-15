import pytest

from lamon import db

from sqlalchemy.orm.exc import NoResultFound

from . import FakeWatcher

from tests import flask, watcher_model, session

@pytest.fixture
def fake_watcher(watcher_model, flask):
    yield watcher_model
    try:
        flask.watcher_manager.stop(model=watcher_model)
    except ValueError:
        pass

class TestManager():
    """ Test Watcher management """

    def test_is_running(self, fake_watcher, flask):
        """ Test is_running mechanism """
        assert not flask.watcher_manager.is_running(id=fake_watcher.id)
        assert not flask.watcher_manager.is_running(model=fake_watcher)

        flask.watcher_manager.start(model=fake_watcher)

        assert flask.watcher_manager.is_running(id=fake_watcher.id)
        assert flask.watcher_manager.is_running(model=fake_watcher)

        flask.watcher_manager.stop(model=fake_watcher)

        assert not flask.watcher_manager.is_running(id=fake_watcher.id)
        assert not flask.watcher_manager.is_running(model=fake_watcher)


class TestManagerStart():
    """ Test Watcher startup """

    def test_start_id(self, fake_watcher, flask):
        """ Test regular starting """
        flask.watcher_manager.start(id=fake_watcher.id)
        assert flask.watcher_manager.is_running(id=fake_watcher.id)

    def test_already_running(self, fake_watcher, flask):
        """ Test starting already running watcher """
        with pytest.raises(ValueError):
            flask.watcher_manager.start(id=fake_watcher.id)
            flask.watcher_manager.start(id=fake_watcher.id)

    def test_nonexistent(self, fake_watcher, flask):
        """ Test starting a watcher not present in the database """
        with pytest.raises(NoResultFound):
            flask.watcher_manager.start(id=fake_watcher.id+1)


class TestManagerStop():
    """ Test Watcher shutdown """

    def test_stop(self, fake_watcher, flask):
        """ Test regular stop """
        flask.watcher_manager.start(id=fake_watcher.id)
        flask.watcher_manager.stop(id=fake_watcher.id)
        assert not flask.watcher_manager.is_running(id=fake_watcher.id)

    def test_already_stopped(self, fake_watcher, flask):
        """ Test stopping an not running watcher """
        with pytest.raises(ValueError):
            flask.watcher_manager.stop(id=fake_watcher.id)

    def test_nonexistent(self, fake_watcher, flask):
        """ Test stopping watcher no present in the database """
        with pytest.raises(NoResultFound):
            flask.watcher_manager.stop(id=fake_watcher.id+1)

class TestManagerReload():
    """ Test Watcher reload """
