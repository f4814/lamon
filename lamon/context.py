import multiprocessing

class Context(object):
    def __init__(self, players):
        self.lock = multiprocessing.Lock()
        self.players = players
