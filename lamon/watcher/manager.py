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

        # Autostart Watchers
        with app.app_context():
            query = db.session.query(WatcherModel)

            current_app.logger.info("Autostarting watchers")
            for m in query.all():
                if m.state == 'RUNNING':
                    self.start(model=m)

    def init_app(self, app, db):
        app.watcher_manager = self

    def start(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        app.logger.info("Starting gamewatcher: {}".format(model))

        if model.state == 'RUNNING':
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

        if model.state != 'STARTED':
            app.logger.warning(
                "Cannot reload watcher: {}".format(model))
            return

        for t in threading.enumerate():
            if isinstance(t, WatcherModel) and t._model.id == model.id:
                t.reload()

    def stop(self, id=None, model=None):
        app = current_app

        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()

        for t in threading.enumerate():
            if isinstance(t, Watcher) and t._model.id == model.id:
                if t._model.state == 'STOPPED':
                    app.logger.warn(
                        "Stopping already stopped watcher: {}".format(model))
                elif t._model.state == 'STOPPING':
                    app.logger.warn(
                        "Watcher already stopping: {}".format(model))
                else:
                    app.logger.info(
                        "Stopping watcher: {}".format(model))
                    t.stop()

                return

        app.logger.warn("Watcher thread not found: {}".format(model))
        model.state = 'STOPPED'
        db.session.commit()
