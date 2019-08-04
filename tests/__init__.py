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


# class BaseTestCase(TestCase):
#     """ Base Test case for lamon. """
#
#     def create_app(self):
#         """ Create the app used for testing """
#         app = create_app('tests/config.toml')
#
#         with app.app_context():
#             db.drop_all()
#             db.create_all()
#
#         return app
#
#     def setUp(self, threadClass='tests.watcher.FakeWatcher'):
#         """ Initialize database and add test data """
#         db.create_all()
#
#         # Add testing data
#         game1 = Game(name='game1')
#         game2 = Game(name='game2')
#         db.session.add(game1)
#         db.session.add(game2)
#
#         admin_role = Role(name='admin')
#         db.session.add(admin_role)
#
#         admin_user = User(username='admin')
#         admin_user.roles.append(admin_role)
#         admin_user.nicknames.append(Nickname(
#             nick='adminGame1', user=admin_user, game=game1))
#         admin_user.nicknames.append(Nickname(
#             nick='adminGame2', user=admin_user, game=game2))
#
#         test1_user = User(username='test1')
#         test1_user.nicknames.append(Nickname(
#             nick='test1Game1', user=test1_user, game=game1))
#         test1_user.nicknames.append(Nickname(
#             nick='test1Game2', user=test1_user, game=game2))
#
#         test2_user = User(username='test2')
#         test2_user.nicknames.append(Nickname(
#             nick='test2Game1', user=test2_user, game=game1))
#         test2_user.nicknames.append(Nickname(
#             nick='test2Game2', user=test2_user, game=game2))
#
#         db.session.add(admin_user)
#         db.session.add(test1_user)
#         db.session.add(test2_user)
#
#         watcher = Watcher(threadClass=threadClass)
#         watcher.config.append(WatcherConfig(key='key1', value='value1'))
#         watcher.config.append(WatcherConfig(key='key3', value='1'))
#         db.session.add(watcher)
#
#         db.session.commit()
#
#         self.game1 = game1
#         self.game2 = game2
#         self.admin_user = admin_user
#         self.test1_user = test1_user
#         self.test2_user = test2_user
#         self.watcher_model = watcher
#
#     def tearDown(self):
#         """ Flush Database """
#         db.drop_all()
#         db.session.remove()

@pytest.fixture
def flask():
    app = create_app('tests/config.toml')
    yield app

    with app.app_context():
        db.drop_all()
        db.session.remove()

# @pytest.fixture(scope="function")
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
