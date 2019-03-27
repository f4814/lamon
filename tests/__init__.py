import threading

from flask import Flask
from flask_user import UserManager, SQLAlchemyAdapter
from flask_testing import TestCase

from lamon import db
from lamon.models import User, Role, Nickname, Game, Watcher


class BaseTestCase(TestCase):
    """ Base Test case for lamon. """

    def create_app(self):
        """ Create the app used for testing """
        app = Flask(__name__)

        # Testing config
        # TODO Move to config file
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['HASH_ROUNDS'] = 1
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'secret'

        db.init_app(app)
        with app.app_context():
            db.drop_all()
            db.create_all()

        # User Manager
        from lamon.models import User
        db_adapter = SQLAlchemyAdapter(db, User)
        user_manager = UserManager(db_adapter, app)

        # Admin views
        from lamon.admin import register_admin
        register_admin(app)

        # Register blueprints
        from lamon.views import register_blueprints
        register_blueprints(app)

        # Register cli commands
        from lamon.cmd import register_cmds
        register_cmds(app)

        # Start Watchers
        from lamon.watcher.manager import WatcherManager
        watcher_manager = WatcherManager(app, db)

        return app

    def setUp(self):
        """ Initialize database and add test data """
        db.create_all()

        # Add testing data
        game1 = Game(name='game1')
        game2 = Game(name='game2')
        db.session.add(game1)
        db.session.add(game2)

        admin_role = Role(name='admin')
        db.session.add(admin_role)

        admin_user = User(username='admin')
        admin_user.roles.append(admin_role)
        admin_user.nicknames.append(Nickname(
            nick='adminGame1', user=admin_user, game=game1))
        admin_user.nicknames.append(Nickname(
            nick='adminGame2', user=admin_user, game=game2))

        test1_user = User(username='test1')
        test1_user.nicknames.append(Nickname(
            nick='test1Game1', user=test1_user, game=game1))
        test1_user.nicknames.append(Nickname(
            nick='test1Game2', user=test1_user, game=game2))

        test2_user = User(username='test2')
        test2_user.nicknames.append(Nickname(
            nick='test2Game1', user=test2_user, game=game1))
        test2_user.nicknames.append(Nickname(
            nick='test2Game2', user=test2_user, game=game2))

        db.session.add(admin_user)
        db.session.add(test1_user)
        db.session.add(test2_user)

        watcher = Watcher(
            state='STOPPED', threadClass='tests.test_watcher.fake.FakeWatcher')
        db.session.add(watcher)

        db.session.commit()

        self.game1 = game1
        self.game2 = game2
        self.admin_user = admin_user
        self.test1_user = test1_user
        self.test2_user = test2_user
        self.watcher_model = watcher

    def tearDown(self):
        """ Flush Database """
        db.drop_all()
        db.session.remove()
