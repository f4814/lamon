from flask import request, redirect
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_user import current_user, login_required, roles_required

from .models import User, Role, Game, Watcher, Nickname, WatcherConfig
from . import db


class AuthModelView(ModelView):
    @login_required
    def is_accessible(self):
        return current_user.has_roles('admin')


class UserView(AuthModelView):
    can_view_details = True

    column_list = ('username', 'roles', 'nicknames')
    inline_models = [Nickname, Role]


class GameView(AuthModelView):
    column_list = ('name', 'nicknames', 'watchers')
    form_excluded_columns = ['scores', 'watchers']
    inline_models = [Nickname]


def register_admin(app):
    admin = Admin(app, name='lamon', template_mode='bootstrap3')

    admin.add_view(UserView(User, db.session))
    admin.add_view(GameView(Game, db.session))
