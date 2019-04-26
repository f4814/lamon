from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_user import roles_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from .. import db
from ..forms import WatcherControlForm, WatcherCreateForm, WatcherEditForm
from ..models import Watcher, Game, WatcherConfig
from ..watcher import load_watcher_class

watcher_blueprint = Blueprint(
    'watchers', __name__, template_folder='templates')


@watcher_blueprint.route('/')
@watcher_blueprint.route('/<int:watcher_id>')
def index(watcher_id=None):
    if watcher_id:
        watcher = Watcher.query.filter(Watcher.id == watcher_id).one()
        form = WatcherControlForm.for_watcher(watcher.id)()

        return render_template('watcher/index_one.html',
                               watcher=watcher, form=form)
    else:
        watchers = []
        show_controls = current_user.is_authenticated and current_user.has_role(
            'admin')

        for watcher in db.session.query(Watcher).all():
            if show_controls:
                form = WatcherControlForm.for_watcher(watcher.id)()
            else:
                form = None

            watchers.append((watcher, form))

        return render_template('watcher/index.html', watchers=watchers,
                               show_controls=show_controls)


@watcher_blueprint.route('/<int:watcher_id>/edit', methods=['GET', 'POST'])
@roles_required(['admin'])
def edit(watcher_id):
    watcher_model = Watcher.query.filter(Watcher.id == watcher_id).one()
    watcher_class = load_watcher_class(watcher_model.threadClass)

    form = WatcherEditForm.load_config(watcher_class, watcher_model)()
    form.game.query = Game.query

    if request.method == 'POST':
        if form.validate_on_submit():
            watcher_model.game = form.data['game']

            # XXX This is probably ugly
            for key, opts in watcher_class.config_keys.items():
                try:
                    watcher_config = WatcherConfig.query.\
                        filter(WatcherConfig.watcher == watcher_model).\
                        filter(WatcherConfig.key == key).\
                        update({'value': form.data[key]})
                except NoResultFound:
                    watcher_config = WatcherConfig(watcher=watcher_model,
                                                   key=key,
                                                   value=form.data[key])
                    db.session.add(watcher_config)

            db.session.commit()

            return redirect(url_for('watchers.index', watcher_id=watcher_id))
        else:
            flash(form.errors, 'warning')

    return render_template('watcher/edit.html', watcher=watcher_model, form=form)


@watcher_blueprint.route('/<int:watcher_id>/stats')
def stats(watcher_id):
    watcher = Watcher.query.filter(Watcher.id == watcher_id).one()
    return render_template('watcher/stats.html', watcher=watcher)


@watcher_blueprint.route('/control', methods=['POST'])
@roles_required(['admin'])
def control():
    app = current_app
    form = WatcherControlForm()

    if form.validate_on_submit():
        try:
            if form.data['start']:
                app.watcher_manager.start(id=form.data['watcher_id'])
                flash('Started watcher', 'success')
            elif form.data['stop']:
                app.watcher_manager.stop(id=form.data['watcher_id'])
                flash('Stopped watcher', 'success')
            elif form.data['reload']:
                app.watcher_manager.reload(id=form.data['watcher_id'])
                flash('Reloaded watcher', 'success')
        except ValueError as e:
            flash(str(e), 'warning')
    else:
        flash(form.errors, 'warning')

    return redirect(request.referrer or url_for('watchers.index'))


@watcher_blueprint.route('/create', methods=['GET', 'POST'])
@roles_required(['admin'])
def create():
    app = current_app

    form = WatcherCreateForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            watcher = Watcher(threadClass=form.data['watcher_class'])
            db.session.add(watcher)
            db.session.commit()
            return redirect(url_for('watchers.edit', watcher_id=watcher.id))

    return render_template('watcher/create.html', form=form)
