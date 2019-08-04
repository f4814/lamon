from flask import Blueprint, render_template, request, current_app, abort, flash, redirect, url_for
from flask_user import roles_required
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from ..models import Game, Watcher, User, Nickname
from .. import db


game_blueprint = Blueprint('games', __name__, template_folder='templates')


@game_blueprint.route('/')
def index():
    games = Game.query.all()
    return render_template('game/index.html', games=list(games))


@game_blueprint.route('/<int:game_id>/')
def index_one(game_id):
    try:
        game = Game.query.filter(Game.id == game_id).one()
    except NoResultFound:
        abort(404)

    watchers = Watcher.query.filter(Watcher.game == game).all()
    players = User.query.filter(User.nicknames.any(Nickname.game == game)).all()
    for player in players: # XXX Don't use this
        setattr(player, 'nickname',
                Nickname.query.\
                    filter(Nickname.user == player, Nickname.game == game)\
                    .one().nick)

    return render_template('game/index_one.html', game=game, watchers=watchers,
                           players=players)
