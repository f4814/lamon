"""
Contains extended flask object and default routes
"""
from flask import Flask

class App(Flask):
    """
    Add default rules to Flask, so Core only has to manage watcher routes
    """
    def __init__(self, config, context):
        self.config = config
        self.context = context
        super().__init__('lamon')

        # Add default rules
        self.add_url_rule('/', 'index', index)


def index():
    return 'in development'
