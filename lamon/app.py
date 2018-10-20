"""
Contains extended flask object and default routes
"""
import logging

from flask import Flask, render_template
from flask_assets import Environment, Bundle

class App(Flask):
    """
    Add default rules to Flask, so Core only has to manage watcher routes
    """
    def __init__(self, config, players):
        super().__init__('lamon', static_folder='css')
        self.logger.setLevel(logging.DEBUG)
        self._config = config
        self._games = []
        self._assets = Environment(self)
        self._players = players

        # Add default rules
        self.add_url_rule('/', 'index', indexPage(self._games))
        self.add_url_rule('/players', 'players', playersPage(self._games))
        self.add_url_rule('/games', 'games', gamesPage(self._games))
        self.add_url_rule('/info', 'info', infoPage(self._games))
        self._assets.url = self.static_url_path

        # SCSS Processing
        scss_default = Bundle('default.scss', filters='pyscss',
                              output='default.css')
        scss_templates = Bundle('templates/default.scss', filters='pyscss',
                                output='templates/default.css')
        self._assets.register('scss_default', scss_default)
        self._assets.register('scss_templates', scss_templates)

    def add_game_rule(self, gameName, gameConfig, hasTemplate):
        """
        Add a game uri to the flask app.
        :param gameName: Game Name
        :type gameName: String
        :param hasTemplate: Is there a special template for this game
        :type hasTemplate: bool
        """
        uri = '/games/' + gameName
        endpoint = 'game_' + gameName
        self._games.append((gameName, endpoint, uri))

        if hasTemplate:
            msgAdd = ''
            route = lambda: render_template(gameName + '.html',
                                            gameConfig=gameConfig,
                                            gameName=gameName,
                                            games=self._games,
                                            players=self._players)
        else:
            msgAdd = ' (default template)'
            route = lambda: render_template('game/default.html',
                                            gameConfig=gameConfig,
                                            gameName=gameName,
                                            games=self._games,
                                            players=self._players)

        self.logger.info('Adding route for ' + uri + msgAdd)
        self.add_url_rule(uri, endpoint, route)


def indexPage(games):
    return lambda: render_template('index.html', games=games)

def playersPage(games):
    return lambda: render_template('players.html', games=games)

def gamesPage(games):
    return lambda: render_template('games.html', games=games)

def infoPage(games):
    return lambda: render_template('info.html', games=games)
