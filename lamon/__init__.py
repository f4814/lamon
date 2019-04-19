import logging

from flask import Flask
from flask.logging import default_handler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter

__version__ = '0.1.0'

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_file='../config.py'):
    app = Flask(__name__)
    app.config['LOGGER_NAME'] = __name__
    app.config['USER_ENABLE_EMAIL'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_pyfile(config_file)

    # Configure logging
    logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # User Manager
    from .models import User
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, app)

    # Admin views
    from .admin import register_admin
    register_admin(app)

    # Register blueprints
    from .views import register_blueprints
    register_blueprints(app)

    # Register cli commands
    from .cmd import register_cmds
    register_cmds(app)

    # Start Watchers
    from .watcher.manager import WatcherManager
    watcher_manager = WatcherManager(app, db)

    return app
