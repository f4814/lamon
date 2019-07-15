from time import sleep

from lamon.watcher import Watcher

class FakeWatcher(Watcher):
    """ Testing watcher. Does nothing """

    config_keys = {}

    def __new__(cls, *args, **kwargs):
        inst = object.__new__(cls)
        if not 'config_keys' in kwargs:
            kwargs['config_keys'] = {
                'key1': {'type': str, 'required': True},
                'key2': {'type': str, 'required': False},
                'key3': {'type': int, 'required': True}}

        inst.config_keys = kwargs['config_keys']
        return inst

    def __init__(self, **kwargs):
        super().__init__(__name__, kwargs['session'], kwargs['model_id'])

    def runner(self):
        while getattr(self, 'shutdown', True):
            pass
