import threading
import logging
import os

import pytest

from flask import Flask
from flask_user import UserManager, SQLAlchemyAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from lamon import db, create_app
from lamon.models import User, Role, Nickname, Game, Watcher, WatcherConfig

from .watcher import FakeWatcher


@pytest.fixture
def flask():
    app = create_app('tests/config.toml')
    yield app

    with app.app_context():
        db.drop_all()
        db.session.remove()

@pytest.fixture
def session(flask):
    with flask.app_context():
        session = scoped_session(sessionmaker(bind=db.engine))
        yield session
    for t in threading.enumerate():
        if isinstance(t, Watcher):
            t.stop()

@pytest.fixture
def watcher_model(session):
    watcher_model = Watcher(threadClass='tests.watcher.FakeWatcher')
    watcher_model.config.append(WatcherConfig(key='key1', value='value1'))
    watcher_model.config.append(WatcherConfig(key='key2', value='value2'))
    watcher_model.config.append(WatcherConfig(key='key3', value='1'))
    session.add(watcher_model)
    session.commit()

    yield watcher_model

@pytest.fixture
def fake_watcher(session, watcher_model):
    watcher = FakeWatcher(session=session, model_id=watcher_model.id)

    yield watcher

    try:
        watcher.stop()
    except:
        pass
