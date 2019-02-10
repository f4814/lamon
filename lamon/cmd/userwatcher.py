import click
from flask import current_app
from flask.cli import AppGroup

from lamon.models import UserWatcher
from lamon import db

userwatcher_cli = AppGroup('userwatcher')

@userwatcher_cli.command('create')
def create_userwatcher():
    pass

@userwatcher_cli.command('remove')
def remove_userwatcher():
    pass

@userwatcher_cli.command('start')
def start_userwatcher():
    pass

@userwatcher_cli.command('stop')
def stop_userwatcher():
    pass
