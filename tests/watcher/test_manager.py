import pytest

from sqlalchemy.orm.exc import NoResultFound

from lamon import db
from . import FakeWatcher
from tests import flask, watcher_model, session, fake_watcher

@pytest.fixture
def watcher_model_(watcher_model, flask):
    """ Like watcher model. But cleans up after itself """
    yield watcher_model
    try:
        flask.watcher_manager.stop(model=watcher_model)
    except ValueError:
        pass

class TestManager():
    """ Test Watcher management """

    def test_is_running(self, watcher_model_, flask):
        """ Test is_running mechanism """
        assert not flask.watcher_manager.is_running(id=watcher_model_.id)
        assert not flask.watcher_manager.is_running(model=watcher_model_)

        flask.watcher_manager.start(model=watcher_model_)

        assert flask.watcher_manager.is_running(id=watcher_model_.id)
        assert flask.watcher_manager.is_running(model=watcher_model_)

        flask.watcher_manager.stop(model=watcher_model_)

        assert not flask.watcher_manager.is_running(id=watcher_model_.id)
        assert not flask.watcher_manager.is_running(model=watcher_model_)


class TestManagerStart():
    """ Test Watcher startup """

    def test_start_id(self, watcher_model_, flask):
        """ Test regular starting """
        flask.watcher_manager.start(id=watcher_model_.id)
        assert flask.watcher_manager.is_running(id=watcher_model_.id)

    def test_already_running(self, watcher_model_, flask):
        """ Test starting already running watcher """
        with pytest.raises(ValueError):
            flask.watcher_manager.start(id=watcher_model_.id)
            flask.watcher_manager.start(id=watcher_model_.id)

    def test_nonexistent(self, watcher_model_, flask):
        """ Test starting a watcher not present in the database """
        with pytest.raises(NoResultFound):
            flask.watcher_manager.start(id=watcher_model_.id+1)


class TestManagerStop():
    """ Test Watcher shutdown """

    def test_stop(self, watcher_model_, flask):
        """ Test regular stop """
        flask.watcher_manager.start(id=watcher_model_.id)
        flask.watcher_manager.stop(id=watcher_model_.id)
        assert not flask.watcher_manager.is_running(id=watcher_model_.id)

    def test_already_stopped(self, watcher_model_, flask):
        """ Test stopping an not running watcher """
        with pytest.raises(ValueError):
            flask.watcher_manager.stop(id=watcher_model_.id)

    def test_nonexistent(self, watcher_model_, flask):
        """ Test stopping watcher no present in the database """
        with pytest.raises(NoResultFound):
            flask.watcher_manager.stop(id=watcher_model_.id+1)
