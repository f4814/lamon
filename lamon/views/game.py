from flask import Blueprint, render_template, request, current_app, abort, flash, redirect, url_for
from flask_user import roles_required
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from ..models import Game, Watcher, User, Nickname
from ..forms.game import CreateUpdateForm
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
    nicknames = []
    for player in players: # XXX Don't use this
        setattr(player, 'nickname',
                Nickname.query.\
                    filter(Nickname.user == player, Nickname.game == game)\
                    .one().nick)

    return render_template('game/index_one.html', game=game, watchers=watchers,
                           players=players, nicknames=nicknames)


@game_blueprint.route('/<int:game_id>/edit', methods=['GET', 'POST'])
@roles_required(['admin'])
def edit(game_id):
    try:
        game = Game.query.filter(Game.id == game_id).one()
    except NoResultFound:
        abort(404)

    form = CreateUpdateForm()
    # form.name.defaut = game.name
    # form.process()

    if request.method == 'POST':
        if form.validate_on_submit():
            game.name = form.data['name']

            try:
                db.session.commit()
            except IntegrityError:
                flash('Name already taken', 'danger')

            return redirect(url_for('games.index_one', game_id=game.id))
        else:
            flash(form.errors, 'warning')

    return render_template('game/edit.html', form=form)


@game_blueprint.route('/create', methods=['GET', 'POST'])
@roles_required(['admin'])
def create():
    form = CreateUpdateForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            game = Game(name=form.data['name'])

            try:
                db.session.add(game)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('Name already taken', 'danger')
        else:
            flash(form.errors, 'warning')

    return render_template('game/create.html', form=form)
