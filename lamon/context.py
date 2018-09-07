"""
Thread safe global player context.
"""
import multiprocessing

class Context():
    """
    Thread safe global player variables.
    This is modified by the spawned game watchers
    """
    def __init__(self, players):
        self.lock = multiprocessing.Lock()
        self.players = players
