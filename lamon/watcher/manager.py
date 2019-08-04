import logging

from flask import current_app
from sqlalchemy.orm import scoped_session, sessionmaker

from ..models import Watcher as WatcherModel
from ..watcher import Watcher, load_watcher_class


class WatcherManager():
    """ Manage watchers in a Flask application.

    :param app: Flask app to bind to
    :param db: Flask-SQLAlchemy Database to use
    """

    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self._watchers = {}

        if app:
            self.init_app(app, db)
        else:
            self.logger = logging.getLogger('lamon.watcher_manager')

    def init_app(self, app, db):
        """ Attach to application

        :param app: Flask app to attach to
        :param db: Flask-SQLAlchemy Database to use
        """
        app.watcher_manager = self
        self.db = db
        self.logger = app.logger.getChild('watcher_manager')

    def start(self, id=None, model=None):
        """ Start a watcher.

        Either id or model is required as argument

        :type id: int
        :param id: Database id of watcher (Default value = None)

        :type model: :class:`lamon.model.Watcher`
        :param model: Database model of watcher (Default value = None)

        :raises ValueError: When watcher is already running
        :raises TypeError: When threadClass of watcher model is no subclass of
            Watcher
        :raises KeyError: When a required config-key is missing
        """
        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        if id in self._watchers:
            self.logger.warning(f'Cannot start already running watcher: {model}')
            raise ValueError(f'Cannot start watcher (id={id}). Already running.')

        self.logger.info(f'Starting gamewatcher: {model}')

        # Create db session not connected to flask
        session = scoped_session(sessionmaker(bind=self.db.engine))

        watcher_ = load_watcher_class(model.threadClass)
        watcher = watcher_(session=session, model_id=id)

        self._watchers[id] = watcher
        watcher.start()

    def restart(self, **kwargs):
        """ Call stop and then start on watcher. Arguments are

        :type id: int
        :param id: Database id of watcher (Default value = None)

        :type model: :class:`lamon.model.Watcher`
        :param model: Database model of watcher (Default value = None)

        :raises ValueError: When watcher is not running
        :raises TypeError: When threadClass of watcher model is no subclass of
            Watcher
        :raises KeyError: When a required config-key is missing
        """
        self.stop(**kwargs)
        self.start(**kwargs)

    def stop(self, id=None, model=None):
        """ Stop a watcher

        Either id or model is required as argument

        :type id: int
        :param id: Database id of watcher (Default value = None)

        :type model: :class:`lamon.model.Watcher`
        :param model: Database model of watcher (Default value = None)

        :raises ValueEror: When watcher is not running
        """
        if id is not None:
            model = WatcherModel.query.filter(WatcherModel.id == id).one()
        elif model is not None:
            id = model.id

        if id in self._watchers:
            self.logger.info(f'Stopping watcher: {model}')
            self._watchers[id].stop()
            self._watchers.pop(id)
        else:
            self.logger.warning(f'Watcher thread not found: {model}')
            raise ValueError(f'Cannot stop watcher (id={id}). Not running')

    def is_running(self, id=None, model=None):
        """ Check if given watcher is currently running

        Either id or model is required as argument

        :type id: int
        :param id: Database id of watcher (Default value = None)

        :type model: :class:`lamon.model.Watcher`
        :param model: Database model of watcher (Default value = None)

        :returns: :class:`bool`
        """
        if id is None:
            id = model.id

        return id in self._watchers
