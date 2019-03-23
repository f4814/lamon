from time import sleep

from lamon.watcher import Watcher

class FakeWatcher(Watcher):
    """ Testing watcher. Does nothing """

    def __init__(self, model, configKeys):
        super().__init__(model, __name__, configKeys)

    def runner(self):
        while getattr(self, 'shutdown', True):
            pass
