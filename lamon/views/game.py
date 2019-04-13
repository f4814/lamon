from flask import Blueprint, render_template, request, current_app
from ..models import Game


game_blueprint = Blueprint('games', __name__, template_folder='templates')


@game_blueprint.route('/')
def index():
    return render_template('game/index.html')


@game_blueprint.route('/stats/')
@game_blueprint.route('/stats/<int:game_id>')
def stats(game_id=None):
    if game_id is None:
        games = Game.query.all()
        return render_template('game/stats.html', games=games)
    else:
        game = Game.query.filter(Game.id == game_id).one()
        return render_template('game/stats_one.html', game=game)
