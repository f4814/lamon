"""
Thread safe global player context.
"""
import multiprocessing

class Context():
    """
    Thread safe global player variables.
    This is modified by the spawned game watchers
    :param players: Array of players
    :type players: list
    :param config: Configuration
    :type config: dict
    """
    def __init__(self, players, config=None):
        self.lock = multiprocessing.Lock()
        self.players = players
        self.config = config
