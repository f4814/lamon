import sys

from abc import ABC, abstractmethod
from threading import Thread
from importlib import import_module
from logging import getLogger, StreamHandler
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from datetime import datetime

from lamon import db
from ..models import Watcher as WatcherModel
from ..models import Nickname, Event, WatcherConfig, EventType, User


class Watcher(ABC, Thread):
    """ Abstract watcher class. Has to be extended to create a "real"
    watcher plugin.

    :type logName: :class:`str`
    :param logName: Name of the logger used by the watcher.
        When extending using __name__ is a good idea

    :type config_keys: :class:`dict`
    :attribute config_keys: Dict keys are config keys. Values is a dict
        containing datatype (`type` key) and wether it is required (`required` key)

    :type session: :class:`sqlalchemy.orm.session.Session`
    :param session: SQLAlchemy session to access the database. You probably
        want a scoped_session

    :type model_id: :class:`int`
    :param model_id: The database id (primary key) of the model.

    :raises TypeError: When initialized with a model whose threadClass does
        not fit the object
    """
    config_keys = {}

    def __init__(self, logName, session=None, model_id=None):
        self._session = session
        self._model_id = model_id
        self.config = {}

        # Setup logger
        self.logger = getLogger(logName)

        # Check for correct model
        qualname = type(self).__module__ + "." + type(self).__name__
        if qualname != self._model.threadClass:
            raise TypeError("""Cannot initalize watcher of class {} with model
                            where threadClass == {}""".
                            format(qualname, self._model.threadClass))

        self.logger.propagate = False
        self.reload()
        self.logger.propagate = True

        # Initialize threading.Thread
        super().__init__(name='Watcher-{}'.format(self._model.id))

    def run(self):
        """ Runs Watcher.runner in a new thread."""
        # Log start
        self.logger.info('Started watcher (id={})'.format(self._model_id))
        self.add_event(Event(type=EventType.WATCHER_START))

        try:
            self.runner()
        except Exception as e:
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

    def reload(self):
        """ Reload all config keys (specified in Watcher.config_keys)
        """
        for key, value in self.config_keys.items():
            query = self._session.query(WatcherConfig).\
                filter(WatcherConfig.watcherID == self._model_id).\
                filter(WatcherConfig.key == key)
            try:
                self.config[key] = value['type'](query.one().value)
                self.logger.debug(
                    "Reload: {} = {}".format(key, self.config[key]))
            except NoResultFound:
                if value['required']:
                    self.logger.warning(
                        "No config w/ key found: {}".format(key))
                else:
                    self.logger.debug("Optional key {} not found".format(key))

        self.logger.info("Reloaded Watcher (id={})".format(self._model.id))
        self.add_event(Event(type=EventType.WATCHER_RELOAD))

    def add_score(self, nickname, score):
        """ Add a score to the user.

        This is a convenience function over :meth:`add_event`and
        :meth:`get_user`

        :type nickname: str
        :param nickname: Nickname of the user

        :type score: int or float
        :param score: **Absolute** score of the user

        :raises ValueError: When no user with the given nickname is found
        """
        user = self.get_user(nickname)
        self.add_event(Event(userID=user.id, gameID=self._model.gameID,
                             type=EventType.USER_SCORE, info=str(score)))

    def add_event(self, event):
        """ Add a event to the database

        :type event: lamon.models.Event
        :param event: Event to add to the database. event.watcherID and
            event.time are set by this function
        """
        event.watcherID = self._model_id

        if event.time is None:
            event.time = datetime.now()

        self._session.add(event)
        self._session.commit()

        self.logger.debug(str(event))

    def get_user(self, nickname):
        """ Get the :class:`lamon.models.User` with the associated Nickname

        :type nickname: str
        :param nickname: Nickname

        :raises ValueError: When no user with the given nickname is found
        """
        query = self._session.query(User).join(Nickname).\
            filter(Nickname.nick == nickname).\
            filter(Nickname.gameID == self._model.game.id)

        try:
            return query.one()
        except NoResultFound:
            raise ValueError("No user with given nickname ({}) found".
                             format(nickname))

    def stop(self):
        """ Stops the watcher """
        self.logger.info("Stopping watcher")
        self.shutdown = False

        self.join()
        self.logger.debug("Watcher thread stopped")

        self.add_event(Event(type=EventType.WATCHER_STOP))

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
        raise TypeError(
            "{} is not a subclass of watcher".format(str(watcher_)))

    return watcher_
