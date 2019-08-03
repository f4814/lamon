from flask import Blueprint, jsonify, current_app

stats_blueprint = Blueprint('stats', __name__, template_folder='templates')

@game_blueprint.route('/')
def index():
    pass
