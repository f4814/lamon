import click
from flask.cli import AppGroup

from lamon.models import User, Game, Nickname
from lamon import db

nick_cli = AppGroup('nick')

@nick_cli.command('add')
@click.argument('name')
@click.argument('game')
@click.argument('nick')
def add_nick_user(name, game, nick):
    queryUser = db.session.query(User).filter(User.username == name)
    queryGame = db.session.query(Game).filter(Game.name == game)

    user = queryUser.one()
    game = queryGame.one()

    user.nicknames.append(Nickname(nick=nick, game=game))
    db.session.commit()

@nick_cli.command('remove')
@click.argument('name')
@click.argument('game')
@click.argument('nick')
def remove_nick(name, game, nick):
    queryUser = db.session.query(User).filter(User.username == name)
    user = queryUser.one()

    queryGame = db.session.query(Game).filter(Game.name == game)
    game = queryGame.one()

    queryNickname = db.session.query(Nickname).filter(Nickname.user == user).\
        filter(Nickname.nick == nick).filter(Nickname.game == game)
    nickname = queryNickname.one()

    db.session.delete(nickname)
    db.session.commit()

@nick_cli.command('change')
@click.argument('name')
@click.argument('game')
@click.argument('old_nick')
@click.argument('new_nick')
def change_nick(game, name, old_nick, new_nick):
    queryUser = db.session.query(User).filter(User.username == name)
    user = queryUser.one()

    queryGame = db.session.query(Game).filter(Game.name == game)
    game = queryGame.one()
    queryNickname = db.session.query(Nickname).\
        filter(Nickname.user == user).\
        filter(Nickname.game == game).\
        filter(Nickname.nick == old_nick)

    nickname = queryNickname.one()
    nickname.nick = new_nick
    db.session.commit()
