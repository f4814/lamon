from flask import Blueprint, render_template, request


game_blueprint = Blueprint('games', __name__, template_folder='templates')


@game_blueprint.route('/')
def index():
    return render_template('game/index.html')


@game_blueprint.route('/stats/')
@game_blueprint.route('/stats/<int:game_id>')
def stats(game_id=None):
    return render_template('game/stats.html')
