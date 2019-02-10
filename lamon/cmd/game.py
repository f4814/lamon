import click
from flask import current_app
from flask.cli import AppGroup

from lamon.models import Game
from lamon import db

game_cli = AppGroup('game')

@game_cli.command('create')
@click.argument('name')
def create_game(name):
    db.session.add(Game(name=name))
    db.session.commit()


@game_cli.command('remove')
@click.argument('name')
def remove_game(name):
    query = db.session.query(Game).filter(Game.name == name)
    game = query.one()

    db.session.remove(game)
    db.session.commit()
