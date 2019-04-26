import logging
import logging.config
import time
import toml

from flask import Flask, request
from flask.logging import default_handler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from sqlalchemy import event
from sqlalchemy.engine import Engine

__version__ = '0.1.0'

db = SQLAlchemy()
migrate = Migrate()


def dictDefault(d, default):
    """ Load default values into a dict """
    if isinstance(d, dict):
        for key, value in default.items():
            if key not in d:
                d[key] = value
            else:
                if isinstance(d[key], dict) and isinstance(default[key], dict):
                    d[key] = dictDefault(d[key], default[key])

    return d


def load_config_file(config_file):
    """ Load a configuration file """
    default_config = {
        'logging': {
            'version': 1,
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            },
            'loggers': {
                'lamon.db': {
                    'level': 'WARNING'
                },
                'flask.app.watcher_manager': {
                    'level': 'WARNING'
                },
                'flask.app.requests': {
                    'level': 'WARNING'
                }
            },
            'formatters': {
                'default': {
                    'format': '%(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'default'
                }
            }
        }
    }

    config = dictDefault(toml.load(config_file), default_config)

    config['flask'] = {}
    config['flask']['SECRET_KEY'] = config['database']['secret_key']
    config['flask']['SQLALCHEMY_DATABASE_URI'] = config['database']['database_uri']

    for key, value in config['app'].items():
        config['flask'][key.upper()] = value

    return config


def create_app(config_file='config.toml'):
    # Load config
    config = load_config_file(config_file)

    # Configure logging
    logging.config.dictConfig(config['logging'])

    # Create Flask
    app = Flask(__name__)
    app.config.from_mapping(config['flask'])
    app.config['USER_ENABLE_EMAIL'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Request logging
    @app.after_request
    def log_request(response):
        logger = app.logger.getChild('requests')
        logger.debug("{} - {} - {}".format(request.method,
                                           response.status_code, request.url))
        return response

    # DB logging
    db_logger = logging.getLogger("lamon.db")

    if db_logger.level is not logging.NOTSET and db_logger.level > logging.DEBUG:
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement,
                                  parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement,
                                 parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            if total > 0.01:
                db_logger.debug("Query Complete: %s", statement)
                db_logger.debug("Total Time: %f", total)

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
