import threading

from flask import current_app
from sqlalchemy.orm import scoped_session, sessionmaker

from ..models import Watcher as WatcherModel
from ..watcher import Watcher, load_watcher_class


class WatcherManager():
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self._watchers = {}

        if app:
            self.init_app(app, db)

    def init_app(self, app, db):
        app.watcher_manager = self
        self.db = db

    def start(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        if id in self._watchers:
            app.logger.warning(
                "Cannot start already running watcher: {}".format(model))
            raise ValueError(
                "Cannot start watcher (id={}). Already running.".format(id))

        app.logger.info("Starting gamewatcher: {}".format(model))

        # Create db session not connected to flask
        session = scoped_session(sessionmaker(bind=self.db.engine))

        watcher_ = load_watcher_class(model.threadClass)
        watcher = watcher_(session=session, model_id=id)

        self._watchers[id] = watcher
        watcher.start()

    def reload(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        if id in self._watchers:
            self._watchers[id].reload()
        else:
            app.logger.warning("Cannot reload watcher: {}".format(model))
            raise ValueError(
                "Cannot reload watcher (id={}). Not running".format(id))

    def stop(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        if id in self._watchers:
            app.logger.info("Stopping watcher: {}".format(model))
            self._watchers[id].stop()
            self._watchers.pop(id)
        else:
            app.logger.warning("Watcher thread not found: {}".format(model))
            raise ValueError(
                "Cannot stop watcher (id={}). Not running".format(id))

    def is_running(self, id=None, model=None):
        app = current_app

        if id is None:
            id = model.id

        return id in self._watchers
