"""
Contains extended flask object and default routes
"""
from flask import Flask

class App(Flask):
    """
    Add default rules to Flask, so Core only has to manage watcher routes
    """
    def __init__(self, config, sqlCursor):
        self.config = config
        self.sqlCursor = sqlCursor
        super().__init__('lamon')

        # Add default rules
        self.add_url_rule('/', 'index', index)


def index():
    return 'in development'

def gameRoute(gameName):
    return (lambda: render_template('tepmlates/' + gameName, gameName))

def defaultRoute(gameName):
    return (lambda: 'testing')
