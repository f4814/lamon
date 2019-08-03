from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, abort
from flask_user import roles_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from .. import db
from ..forms.watcher import ControlForm, CreateForm, EditForm
from ..models import Watcher, Game, WatcherConfig
from ..watcher import load_watcher_class

watcher_blueprint = Blueprint(
    'watchers', __name__, template_folder='templates')


@watcher_blueprint.route('/')
def index():
    watchers = Watcher.query.all()
    return render_template('watcher/index.html', watchers=list(watchers))


@watcher_blueprint.route('/<int:watcher_id>')
def index_one(watcher_id):
    try:
        watcher = Watcher.query.filter(Watcher.id == watcher_id).one()
    except NoResultFound:
        abort(404)

    form = ControlForm()

    return render_template('watcher/index_one.html',
                           watcher=watcher, form=form)


@watcher_blueprint.route('/<int:watcher_id>/edit', methods=['GET', 'POST'])
@roles_required(['admin'])
def edit(watcher_id):
    watcher_model = Watcher.query.filter(Watcher.id == watcher_id).one()
    watcher_class = load_watcher_class(watcher_model.threadClass)

    form = EditForm.load_config(watcher_class, watcher_model)()
    form.game.query = Game.query

    if request.method == 'POST':
        if form.validate_on_submit():
            watcher_model.game = form.data['game']

            for key, opts in watcher_class.config_keys.items():
                try:
                    config = WatcherConfig.query.\
                        filter(WatcherConfig.watcher == watcher_model).\
                        filter(WatcherConfig.key == key).one()
                    config.key = form.data[key]
                except NoResultFound:  # Key has not been added yet
                    config = WatcherConfig(
                        watcher=watcher_model, key=key, value=form.data[key])
                    db.session.add(config)

            db.session.commit()

            return redirect(url_for('watchers.index', watcher_id=watcher_id))
        else:
            flash(form.errors, 'warning')

    return render_template('watcher/edit.html', watcher=watcher_model, form=form)


@watcher_blueprint.route('/<int:watcher_id>/control', methods=['POST'])
@roles_required(['admin'])
def control(watcher_id):
    app = current_app
    form = ControlForm()

    if form.validate_on_submit():
        try:
            if form.data['start']:
                app.watcher_manager.start(id=watcher_id)
                flash('Started watcher', 'success')
            elif form.data['stop']:
                app.watcher_manager.stop(id=watcher_id)
                flash('Stopped watcher', 'success')
            elif form.data['reload']:
                app.watcher_manager.reload(id=watcher_id)
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

    form = CreateForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            watcher = Watcher(threadClass=form.data['watcher_class'])
            db.session.add(watcher)
            db.session.commit()
            return redirect(url_for('watchers.edit', watcher_id=watcher.id))

    return render_template('watcher/create.html', form=form)
