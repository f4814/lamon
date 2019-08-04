import sys

from abc import ABC, abstractmethod
from threading import Thread
from importlib import import_module
from logging import getLogger, StreamHandler
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from lamon import db
from .events import Watcher__Events
from ..models import Watcher as WatcherModel
from ..models import Nickname, WatcherConfig, User


class Watcher(ABC, Thread, Watcher__Events):
    """ Abstract watcher class. Has to be extended to create a "real"
    watcher plugin.

    :type logName: :class:`str`
    :param logName: Name of the logger used by the watcher.
        When extending using __name__ is a good idea

    :type session: :class:`sqlalchemy.orm.session.Session`
    :param session: SQLAlchemy session to access the database. You probably
        want a scoped_session

    :type model_id: :class:`int`
    :param model_id: The database id (primary key) of the model.

    :raises TypeError: When initialized with a model whose threadClass does
        not fit the object
    :raises KeyError: When a required config-key is missing
    """

    config_keys = {}
    """ Plugins can specify which configuration values the user should be able
    to set with this dict.

    Each key of the dict is the name of a configuration key in the database.
    The value is a dict with the following keys:

        * *type*: Function to typecast a string (from the database) into
            a usable value (Required)
        * *required*: Whether this value is required (Required)
        * *hint*: Text to show when editing this configuration value (Optional)
        * *warning*: Warning to show when editing this configuration value (Optional)

    Example:

    .. code-block:: python

        config_keys = {'address': {'type': 'str', 'required': True},
                    'port': {'type': int, 'required': True},
                    'timeout': {'type': int, 'required': True},
                    'app_id:': {'type': int, 'required': True,
                                'hint':
                                \"\"\"this is the app ID of the client, not the
                                server. For example, for Team Fortress 2 440 has
                                to be used instead of 232250 which is the ID of
                                the server software.\"\"\"}}
    """

    def __init__(self, logName, session=None, model_id=None):
        self._session = session
        self._model_id = model_id
        self.config = {}

        # Setup logger
        self.logger = getLogger(logName)

        # Check for correct model
        qualname = type(self).__module__ + "." + type(self).__name__
        if qualname != self._model.threadClass:
            raise TypeError(f"""Cannot initalize watcher of class {qualname} with
                            model where threadClass == {self._model.threadClass}
                            """)

        # Load config_keys into self.config
        self.logger.debug(f'Loading watcher configuration')
        for key, value in self.config_keys.items():
            query = self._session.query(WatcherConfig).\
                filter(WatcherConfig.watcherID == self._model_id).\
                filter(WatcherConfig.key == key)
            try:
                self.config[key] = value['type'](query.one().value)
                self.logger.debug(f'Config: {key} = {self.config[key]}')
            except NoResultFound:
                if value['required']:
                    self.logger.warning(f'No config w/ key found: {key}')
                    raise KeyError(f'Watcher has no {key} config-key')

                self.logger.debug(f'Optional key {key} not found')

        # Initialize threading.Thread
        super().__init__(name=f'Watcher-{self._model.id}')

    def run(self):
        """ Runs Watcher.runner in a new thread."""
        # Log start
        self.logger.info(f'Started watcher (id={self._model.id})')
        self.start_event()

        try:
            self.runner()
        except Exception as e:
            self.exception_event(e)
            self.logger.exception(e)

        self._session.commit()
        self._session.close()

    @abstractmethod
    def runner(self):
        """ Main loop. Has to be overwritten.

        This function is supposed to run until Watcher.shutdown is set to true
        or an error occurs. Restarting and error logging is handled by
        Watcher.run

        Errors indicating a connection problem should not crash this function.
        """

    @property
    def _model(self):
        """ Since some database systems don't like multithreaded access
        this reloads the model at every access.
        """
        query = self._session.query(WatcherModel).\
            filter(WatcherModel.id == self._model_id)
        return query.one()

    def stop(self):
        """ Stops the watcher """
        self.logger.info("Stopping watcher")
        self.shutdown = False

        self.join()
        self.logger.debug("Watcher thread stopped")

        self.stop_event()

        self._session.commit()
        self._session.close()
        self.logger.debug("DB session closed")

    def __repr__(self):
        return str(self._model)


class WatcherException(Exception):
    """ Exception to be raised when a watcher encounters problems. (Provided
    there is no better Exception)
    """
    pass


def load_watcher_class(className):
    """ Dynamically load a class extending watcher into the module namespace.
    This is used by WatcherManager to load the class at watcher startup.

    :type className: str
    :param className: Name of the class (with module) to be loaded

    :raises TypeError: When the provided class does not extend :class:`Watcher`

    :returns: Subclass of :class:`Watcher`
    """
    module = import_module(".".join(className.split(".")[:-1]))

    watcher_ = getattr(module, className.split(".")[-1])

    if not issubclass(watcher_, Watcher):
        raise TypeError(f'{watcher_} is not a subclass of watcher')

    return watcher_
