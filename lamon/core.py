import yaml
import importlib
import multiprocessing

from player import Player
from context import Context

class Core(object):
    """ Core object. Spawns threads. """
    def __init__(self, configFile):
        # Load config
        print('Loading config file: ' + configFile)
        with open(configFile, 'r') as c:
            self.config = yaml.load(c)
        self.games = {}

        # Load players
        players = []
        for key, value in self.config['players'].items():
            p = Player(key, value['nicks'])
            players.append(p)

        # Create Context
        self.context = Context(players)

        # Load games
        for g in self.config['games']:
            self.loadGame(g)

    def loadGame(self, gameName):
        """
        Load the game specified by config.
        :param config: Game config read from yaml
        :type config: dict
        """
        if not gameName in self.config['games']:
            print('Game ' + gameName + ' not configured. Skipping.')
            return

        if gameName in self.games:
            print('Game ' + gameName + ' already running. Skipping.')
            return

        # Import module
        module = importlib.import_module('game.' + gameName)
        game_ = getattr(module, gameName)
        print('Loaded module: game.' + gameName)

        # Create game Object
        game = game_(self.config['games'][gameName])

        # Dispatch
        p = multiprocessing.Process(target=game.dispatch, 
                                    name=gameName + '_watcher', 
                                    args=(self.context,))
        self.games[gameName] = (game, p)
        p.start()
        print('Watching game ' + gameName)

    def close(self):
        """
        Stop all threads and close all connections
        """
        for game, p in self.games:
            print('Terminating ' + game.name + ' game watcher')
            p.terminate() # TODO use queue
            game.close()
