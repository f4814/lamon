import sys

from abc import ABC, abstractmethod
from threading import Thread
from importlib import import_module
from logging import getLogger, StreamHandler

from lamon import db
from ..models import Watcher as WatcherModel


class Watcher(ABC, Thread):
    def __init__(self, model, logName):
        super().__init__(name='Watcher-{}'.format(model.id))
        self.model = model
        self.logger = getLogger(logName)
        self.logger.setLevel(10)
        self.logger.addHandler(StreamHandler(sys.stdout))

        if model.state != 'RUNNING':
            model.state = 'RUNNING'
            db.session.commit()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def load_config(self):
        pass

    def reload(self):
        pass

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


def create_watcher_object(watcher, className):
    module = import_module(".".join(className.split(".")[:-1]))

    watcher_ = getattr(module, className.split(".")[-1])

    return watcher_
