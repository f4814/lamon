from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, abort
from flask_user import roles_required
from sqlalchemy.orm.exc import NoResultFound

from ..models import Watcher, Game

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

    return render_template('watcher/index_one.html', watcher=watcher)


@watcher_blueprint.route('/<int:id>/start')
@roles_required(['admin'])
def start(id):
    try:
        current_app.watcher_manager.start(id=id)
    except ValueError as e:
        flash(str(e), 'warning')
    except KeyError as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('watchers.index_one', watcher_id=id))

@watcher_blueprint.route('/<int:id>/stop')
@roles_required(['admin'])
def stop(id):
    try:
        current_app.watcher_manager.stop(id=id)
    except ValueError as e:
        flash(str(e), 'warning')
    return redirect(request.referrer or url_for('watchers.index_one', watcher_id=id))

@watcher_blueprint.route('/<int:id>/restart')
@roles_required(['admin'])
def restart(id):
    try:
        current_app.watcher_manager.restart(id=id)
    except ValueError as e:
        flash(str(e), 'warning')
    return redirect(request.referrer or url_for('watchers.index_one', watcher_id=id))
