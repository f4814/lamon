import sys

from abc import ABC, abstractmethod
from threading import Thread
from importlib import import_module
from logging import getLogger, StreamHandler
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from lamon import db
from ..models import Watcher as WatcherModel
from ..models import Nickname, Score, WatcherConfig


class Watcher(ABC, Thread):
    """ Abstract watcher class. Has to be extended to create a "real"
    watcher plugin.

    :type logName: :class:`str`
    :param logName: Name of the logger used by the watcher.
        When extending using __name__ is a good idea

    :type config_keys: :class:`list`
    :param config_keys: Config keys the watcher is looking for in the database

    :type session: :class:`sqlalchemy.orm.session.Session`
    :param session: SQLAlchemy session to access the database. You probably
        want a scoped_session

    :raises TypeError: When initialized with a model whose threadClass does
        not fit the object
    """

    def __init__(self, logName, **kwargs):
        # Get Kwargs
        self.config_keys = kwargs['config_keys']
        self._session = kwargs['session']

        # Setup logger
        self.logger = getLogger(logName)

        # Load Model
        self._model = self._session.query(WatcherModel).\
            filter(WatcherModel.id == kwargs['model_id']).one()

        # Check for correct model
        qualname = type(self).__module__ + "." + type(self).__name__
        if qualname != self._model.threadClass:
            raise TypeError("""Cannot initalize watcher of class {} with model
                            where threadClass == {}""".
                            format(qualname, self._model.threadClass))

        # Load config
        self.config = {}
        for k in self.config_keys:
            self.config[k] = None
        self.reload()

        # Initialize threading.Thread
        super().__init__(name='Watcher-{}'.format(self._model.id))

    def run(self):
        """ Runs Watcher.runner in a new thread."""
        self.reload()

        # Load Model into new thread
        self._session.add(self._model)
        self._session.commit()

        try:
            self.runner()
        except Exception as e:
            self.logger.exception(e)

    @abstractmethod
    def runner(self):
        """ Main loop. Has to be overwritten.

        This function is supposed to run until Watcher.shutdown is set to true
        or an error occurs. Restarting and error logging is handled by
        Watcher.run

        Errors indicating a connection problem should not crash this function.
        """

    def reload(self):
        """ Reload all config keys (specified in Watcher.config_keys)

        This function can be overwritten if typecasting of the config values
        is required. See :class:`SourceEngineWatcher` for an example
        """
        self._model = self._session.query(WatcherModel).\
            filter(WatcherModel.id == self._model.id).one()

        for k in self.config_keys:
            query = self._session.query(WatcherConfig).\
                filter(WatcherConfig.watcherID == self._model.id).\
                filter(WatcherConfig.key == k)
            try:
                self.config[k] = query.one().value
                self.logger.debug("Reload: {} = {}".format(k, self.config[k]))
            except NoResultFound:
                self.logger.warning("No config w/ key found: {}".format(k))

        self.logger.info("Reloaded Watcher (id={})".format(self._model.id))

    def add_score(self, nickname, points):
        """ Add a score to the database.

        :type nickname: str
        :param nickname: Nickname of the player

        :type points: int
        :param points: Points to be added to the players score
        """
        self.logger.debug("Adding {} points to {}".format(points, nickname))
        query = self._session.query(Nickname).\
            filter(Nickname.nick == nickname).\
            filter(Nickname.gameID == self._model.gameID)

        try:
            nickModel = query.One()
        except NoResultFound:
            self.logger.warning("Unknown nickname: {}".format(nickname))
            return

        score = Score(points, game=self._model.game,
                      user=nickModel.user, nick=nickModel)

        self._session.add(score)
        self._session.commit()

    def stop(self):
        """ Stops the watcher """
        self.logger.info("Stopping watcher")
        self.shutdown = False

        self.join()

        self._session.commit()
        self._session.close()

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
