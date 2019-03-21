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
    def __init__(self, model, logName, configKeys):
        super().__init__(name='Watcher-{}'.format(model.id))
        self.configKeys = configKeys
        self.model = model
        self.logger = getLogger(logName)
        self.logger.setLevel(10)
        self.logger.addHandler(StreamHandler(sys.stdout))

        model.state = 'RUNNING'
        db.session.commit()

        self.config = {}
        for k in configKeys:
            self.config[k] = None
        self.reload()

    def run(self):
        try:
            self.runner()
        except Exception as e:
            self.logger.exception(e)

    @abstractmethod
    def runner(self):
        pass

    def reload(self):
        for k in self.configKeys:
            query = db.session.query(WatcherConfig).\
                filter(WatcherConfig.watcherID == self.model.id).\
                filter(WatcherConfig.key == k)
            try:
                self.config[k] = query.one().value
            except NoResultFound:
                self.logger.warning("No config w/ key found: {}".format(k))

    def addScore(self, nickname, points):
        query = db.session.query(Nickname).\
            filter(Nickname.nick == nickname).\
            filter(Nickname.gameID == self.model.gameID)

        try:
            nickModel = query.One()

            score = Score(points, game=self.model.game,
                        user=nickModel.user, nick=nickModel)

            db.session.add(score)
            db.session.commit()
        except NoResultFound:
            self.logger.warning("Unknown nickname: {}".format(nickname))

    def stop(self):
        self.shutdown = False

        query = db.session.query(WatcherModel).filter(
            WatcherModel.id == self.model.id)
        query.update({WatcherModel.state: 'STOPPING'})
        db.session.commit()

        self.join()

        query.update({WatcherModel.state: 'STOPPED'})
        db.session.commit()

    def __repr__(self):
        return str(self.model)


class WatcherException(Exception):
    pass


class ConnectionException(Exception):
    pass


def load_watcher_class(className):
    module = import_module(".".join(className.split(".")[:-1]))

    watcher_ = getattr(module, className.split(".")[-1])

    if not issubclass(watcher_, Watcher):
        raise TypeError("{} is not a subclass of watcher".format(str(watcher_)))

    return watcher_
