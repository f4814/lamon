import click
from flask import current_app
from flask.cli import AppGroup

from lamon.models import Game
from lamon import db

gamewatcher_cli = AppGroup('gamewatcher')

@gamewatcher_cli.command('create')
def create_gamewatcher():
    pass

@gamewatcher_cli.command('remove')
def remove_gamewatcher():
    pass

@gamewatcher_cli.command('start')
def start_gamewatcher():
    pass

@gamewatcher_cli.command('stop')
def stop_gamewatcher():
    pass
