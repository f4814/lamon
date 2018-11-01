"""
Contains the Core object. This is the only module you need to import
"""
import importlib
import multiprocessing
import yaml
import sqlite3
import logging
import re

from gevent.pywsgi import WSGIServer

from .player import Players, PlayerNameError
from .app import App
from .sql import initDatabase

logger = logging.getLogger(__name__)

class Core():
    """ Core object. Spawns threads. """
    def __init__(self, configFile):
        # Load config
        logger.info('Loading config file: ' + configFile)
        with open(configFile, 'r') as config:
            self._config = yaml.load(config)

        self.games = {}

        # Create Sqlite database
        self._sqlConn = sqlite3.connect(self._config['database']['path'])
        initDatabase(self._sqlConn.cursor())

        # Load players
        self.players = Players(self._sqlConn)
        for key, value in self._config['players'].items():
            try:
                self.players.addPlayer(key, value['nicks'])
            except PlayerNameError:
                logger.info('Player ' + key + ' already exists')

        # Initialize flask server
        if self._config['server'] == True:
            self._app = App(self._config, self.players)
        self.server = WSGIServer(('', 3000), self._app)

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
            logger.warning('Game ' + gameName + ' not configured. Skipping.')
            return

        if gameName in self.games:
            logger.warning('Game ' + gameName + ' already running. Skipping.')
            return

        # Import module
        module = importlib.import_module('lamon.game.' + gameName)
        game_ = getattr(module, gameName.upper())
        logger.info('Loaded module: game.' + gameName)

        # Create game Object
        game = game_(self.players, self._config['games'][gameName])

        # Add Flask route
        self._app.add_game_rule(gameName, self._config['games'][gameName],
                                game.hasTemplate)

        # Dispatch
        p = multiprocessing.Process(target=game.dispatch,
                                    name=gameName + '_watcher')
        self.games[gameName] = (game, p)
        p.start()
        logger.info('Watching game ' + gameName)

    def close(self):
        """
        Stop all threads and close all connections
        """
        for game, p in self.games:
            logger.info('Terminating ' + game.name + ' game watcher')
            p.terminate() # TODO use queue
            game.close()
        self._sqlConn.close()
