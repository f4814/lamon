from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_user import current_user, login_required, roles_required

from .models import User, Role, Game, Watcher, Nickname, WatcherConfig
from . import db

class AuthModelView(ModelView):
    @login_required
    def is_accessible(self):
        return current_user.has_roles('admin')

class UserView(AuthModelView):
    column_list = ('username', 'roles', 'nicknames', 'watchers')

class GameView(AuthModelView):
    column_list = ('name', 'nicknames', 'watchers')

class WatcherConfigView(AuthModelView):
    column_list = ('key', 'value', 'watcherID')

def register_admin(app):
    admin = Admin(app, name='lamon')

    admin.add_view(UserView(User, db.session, category='User'))
    admin.add_view(AuthModelView(Nickname, db.session, category='User'))
    admin.add_view(AuthModelView(Role, db.session))
    admin.add_view(GameView(Game, db.session, category='Game'))
    admin.add_view(AuthModelView(Watcher, db.session, category='Watcher'))
    admin.add_view(AuthModelView(WatcherConfig, db.session, category='Watcher'))
