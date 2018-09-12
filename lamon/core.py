"""
Contains the Core object. This is the only module you need to import
"""
import importlib
import multiprocessing
import yaml

from gevent.pywsgi import WSGIServer

from .player import Player
from .context import Context
from .app import App, gameRoute, defaultRoute

class Core():
    """ Core object. Spawns threads. """
    def __init__(self, configFile):
        # Load config
        print('Loading config file: ' + configFile)
        with open(configFile, 'r') as config:
            self.config = yaml.load(config)

        self.games = {}

        # Load players
        players = []
        for key, value in self.config['players'].items():
            player = Player(key, value['nicks'])
            players.append(player)

        # Create Context
        self.context = Context(players)

        # Initialize flask server
        if self.config['server'] == True:
            self.app = App(self.config, self.context)
        self.server = WSGIServer(('', 5000), self.app)

        # Load games
        for game in self.config['games']:
            self.loadGame(game)

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
        module = importlib.import_module('lamon.game.' + gameName)
        game_ = getattr(module, gameName.upper())
        print('Loaded module: game.' + gameName)

        # Create game Object
        game = game_(self.config['games'][gameName])

        # Add Flask route
        print("Adding route for: /game/" + gameName)
        if game.hasTemplate:
            self.app.add_url_rule('/game/' + gameName, gameName,
                                   gameRoute(gameName))
        else:
            self.app.add_url_rule('/game/' + gameName, gameName,
                                   defaultRoute(gameName))

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
