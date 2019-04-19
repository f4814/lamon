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


class WatcherView(AuthModelView):
    column_list = ('threadClass', 'game', 'user', 'config')
    inline_models = [WatcherConfig, ]
    form_choices = {
        'threadClass': [
            ('lamon.watcher.game.source_engine.SourceEngineWatcher',
                'Source Engine Watcher'),
            ('tests.test_watcher.fake.FakeWatcher',
                'Fake Watcher')
        ]
    }

    def get_save_return_url(self, model, is_created=False):
        """ Return the user to edit page after watcher creation. """
        if is_created is True:
            if request.path == self.get_url('.create_view'):
                return self.get_url('.edit_view', id=model.id)+'&created=true'

        return self.get_url('.index_view')

    def create_form(self, obj=None):
        """ The create form should only select the threadClass of the watcher """
        form = super().create_form(obj)
        del form.game
        del form.user
        del form.config
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)

        if request.args.get('created', 'false') == 'true':
            del form.threadClass

        return form


def register_admin(app):
    admin = Admin(app, name='lamon', template_mode='bootstrap3')

    admin.add_view(UserView(User, db.session))
    admin.add_view(GameView(Game, db.session))
    admin.add_view(WatcherView(Watcher, db.session))
