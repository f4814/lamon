from .main import main_blueprint
from .user import user_blueprint
from .game import game_blueprint
from .watcher import watcher_blueprint


def register_blueprints(app):
    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(game_blueprint, url_prefix='/game')
    app.register_blueprint(watcher_blueprint, url_prefix='/watcher')
    # app.register_blueprint(stats_blueprint, url_prefix='/stats')
