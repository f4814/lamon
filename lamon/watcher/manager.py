import threading

from flask import current_app
from sqlalchemy.orm import scoped_session, sessionmaker

from ..models import Watcher as WatcherModel
from ..watcher import Watcher, load_watcher_class

from lamon import db


class WatcherManager():
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db

        if app:
            self.init_app(app, db)

    def init_app(self, app, db):
        app.watcher_manager = self

    def start(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        app.logger.info("Starting gamewatcher: {}".format(model))

        for t in threading.enumerate():
            if isinstance(t, Watcher) and t._model.id == id:
                app.logger.warning(
                    "Cannot start already running watcher: {}".format(model))
                return

        # Create db session not connected to flask
        session = scoped_session(sessionmaker(bind=db.engine))

        watcher_ = load_watcher_class(model.threadClass)
        watcher = watcher_(session=session, model_id=id)
        watcher.start()

    def reload(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        for t in threading.enumerate():
            if isinstance(t, WatcherModel) and t._model.id == model.id:
                t.reload()
                return

        app.logger.warning("Cannot reload watcher: {}".format(model))

    def stop(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        for t in threading.enumerate():
            if isinstance(t, Watcher) and t._model.id == model.id:
                app.logger.info("Stopping watcher: {}".format(model))
                t.stop()
                return

        app.logger.warn("Watcher thread not found: {}".format(model))

    def is_running(self, id=None, model=None):
        app = current_app

        if id is None:
            id = model.id

        for t in threading.enumerate():
            if isinstance(t, Watcher) and t._model.id == id:
                return True

        return False
