from flask import Blueprint, render_template, request, current_app, flash
from flask_user import roles_required

from ..forms import WatcherControlForm
from ..models import Watcher

watcher_blueprint = Blueprint(
    'watchers', __name__, template_folder='templates')


@watcher_blueprint.route('/')
def index():
    return render_template('watcher/index.html')


@watcher_blueprint.route('/stats/')
@watcher_blueprint.route('/stats/<int:watcher_id>')
def stats(watcher_id=None):
    if watcher_id is None:
        watchers = Watcher.query.all()
        return render_template('watcher/stats.html', watchers=watchers)
    else:
        watcher = Watcher.query.filter(Watcher.id == watcher_id).one()
        return render_template('watcher/stats_one.html', watcher=watcher)


@watcher_blueprint.route('/control', methods=['GET', 'POST'])
@roles_required(['admin'])
def control():
    app = current_app

    form = WatcherControlForm()
    form.update_choices()

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                if form.data['action'] == 'START':
                    app.watcher_manager.start(id=form.data['watcherID'])
                    flash('Watcher started successfully', 'success')
                elif form.data['action'] == 'STOP':
                    app.watcher_manager.stop(id=form.data['watcherID'])
                    flash('Watcher stopped successfully', 'success')
                else:  # RELOAD
                    app.watcher_manager.reload(id=form.data['watcherID'])
                    flash('Watcher reloaded successfully', 'success')
            except ValueError as e:
                flash(e, 'warning')

    return render_template('watcher/control.html', form=form)
