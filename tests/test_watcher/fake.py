from time import sleep

from lamon.watcher import Watcher

class FakeWatcher(Watcher):
    """ Testing watcher. Does nothing """

    def __init__(self, **kwargs):
        super().__init__(logName=__name__, config_keys=[], **kwargs)

    def runner(self):
        while getattr(self, 'shutdown', True):
            pass
