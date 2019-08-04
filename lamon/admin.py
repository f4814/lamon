from flask import request, redirect, flash, url_for, current_app
from flask_admin import Admin, expose
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView
from flask_user import current_user
from wtforms import SelectField, HiddenField

from .models import User, Role, Game, Watcher, Nickname, WatcherConfig
from . import db
from .watcher import load_watcher_class


class AuthModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_roles('admin')

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            flash('You are not an admin', 'warning')
            return redirect(url_for('main.index'))

        flash('You have to login to use the admin interface', 'warning')
        return redirect(url_for('user.login'))


class UserView(AuthModelView):
    can_view_details = True

    column_list = ('username', 'roles', 'nicknames')
    column_details_list = ('username', 'roles', 'nicknames', 'events')
    column_searchable_list = ('username',)

    form_excluded_columns = ['events']
    inline_models = [Nickname, Role]

    def on_model_change(self, form, model, is_created):
        model.password = current_app.user_manager.hash_password(model.password)


class GameView(AuthModelView):
    can_view_details = True

    column_list = ('name', 'nicknames', 'watchers')
    column_details_list = ('name', 'nicknames', 'watchers', 'events')
    form_excluded_columns = ['scores', 'watchers', 'events']
    inline_models = [Nickname]


class WatcherView(AuthModelView):
    can_view_details = True

    column_list = ('game', 'info', 'config')
    column_details_list = ('game', 'info', 'config', 'events')
    form_excluded_columns = ['events']
    inline_models = [WatcherConfig]

    form_args = {
        'threadClass': {
            'label': 'Watcher Type',
            'choices': [
                ('lamon.watcher.plugin.source_engine.SourceEngineWatcher',
                 'Source Engine Watcher'),
                ('lamon.watcher.plugin.quake3.Quake3Watcher',
                 'Quake3 Watcher'),
                ('lamon.watcher.plugin.minecraft.MinecraftWatcher',
                 'Minecraft Watcher'),
                ('tests.test_watcher.fake.FakeWatcher',
                 'Fake Watcher')
            ]
        }
    }

    form_overrides = {
        'threadClass': SelectField,
        'config': HiddenField
    }

    column_extra_row_actions = [
        EndpointLinkRowAction('glyphicon glyphicon-play', 'watchers.start'),
        EndpointLinkRowAction('glyphicon glyphicon-stop', 'watchers.stop'),
        EndpointLinkRowAction('glyphicon glyphicon-refresh', 'watchers.restart')
    ]


def register_admin(app):
    admin = Admin(app, name='lamon', template_mode='bootstrap3',
                  base_template='admin/theme.html')

    admin.add_view(UserView(User, db.session))
    admin.add_view(GameView(Game, db.session))
    admin.add_view(WatcherView(Watcher, db.session))
