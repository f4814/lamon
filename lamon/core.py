"""
Contains the Core object. This is the only module you need to import
"""
import importlib
import multiprocessing
import yaml
import sqlite3

from gevent.pywsgi import WSGIServer

from .player import Players
from .app import App, gameRoute, defaultRoute
from .sql import initDatabase

class Core():
    """ Core object. Spawns threads. """
    def __init__(self, configFile):
        # Load config
        print('Loading config file: ' + configFile)
        with open(configFile, 'r') as config:
            self._config = yaml.load(config)

        self.games = {}

        # Create Squlite database
        self._sqlConn = sqlite3.connect(self._config['database']['path'])
        initDatabase(self._sqlConn.cursor())

        # Load players
        self.players = Players(self._sqlConn)
        for key, value in self._config['players'].items():
            self.players.addPlayer(key, value['nicks'])

        # Initialize flask server
        if self._config['server'] == True:
            self._app = App(self._config)
        self.server = WSGIServer(('', 5000), self._app)

        # Load games
        for game in self._config['games']:
            self._loadGame(game)

    def _loadGame(self, gameName):
        """
        Load the game specified by config.
        :param config: Game config read from yaml
        :type config: dict
        """
        if not gameName in self._config['games']:
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
        game = game_(self.players, self._config['games'][gameName])

        # Add Flask route
        print("Adding route for: /game/" + gameName)
        if game.hasTemplate:
            self._app.add_url_rule('/game/' + gameName, gameName,
                                   gameRoute(gameName))
        else:
            self._app.add_url_rule('/game/' + gameName, gameName,
                                   defaultRoute(gameName))

        # Dispatch
        p = multiprocessing.Process(target=game.dispatch,
                                    name=gameName + '_watcher')
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
        self._sqlConn.close()
