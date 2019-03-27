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
    def __init__(self, logName, **kwargs):
        # Get Kwargs
        self.config_keys = kwargs['config_keys']
        self._session = kwargs['session']

        # Setup logger
        self.logger = getLogger(logName)
        self.logger.setLevel(10)
        self.logger.addHandler(StreamHandler(sys.stdout))

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
        self.reload()

        self._session.add(self._model)
        self._session.commit()

        try:
            self.runner()
        except Exception as e:
            self.logger.exception(e)

    @abstractmethod
    def runner(self):
        pass

    def reload(self):
        self._model = self._session.query(WatcherModel).\
            filter(WatcherModel.id == self._model.id).one()

        for k in self.config_keys:
            query = self._session.query(WatcherConfig).\
                filter(WatcherConfig.watcherID == self._model.id).\
                filter(WatcherConfig.key == k)
            try:
                self.config[k] = query.one().value
            except NoResultFound:
                self.logger.warning("No config w/ key found: {}".format(k))

    def add_score(self, nickname, points):
        query = self._session.query(Nickname).\
            filter(Nickname.nick == nickname).\
            filter(Nickname.gameID == self._model.gameID)

        try:
            nickModel = query.One()
        except NoResultFound:
            self.logger.warning("Unknown nickname: {}".format(nickname))

        score = Score(points, game=self._model.game,
                      user=nickModel.user, nick=nickModel)

        self._session.add(score)
        self._session.commit()

    def stop(self):
        self.shutdown = False

        self.join()

        self._session.commit()
        self._session.close()

    def __repr__(self):
        return str(self._model)


class WatcherException(Exception):
    pass


def load_watcher_class(className):
    module = import_module(".".join(className.split(".")[:-1]))

    watcher_ = getattr(module, className.split(".")[-1])

    if not issubclass(watcher_, Watcher):
        raise TypeError(
            "{} is not a subclass of watcher".format(str(watcher_)))

    return watcher_
