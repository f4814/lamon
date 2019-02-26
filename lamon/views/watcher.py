from flask import Blueprint, render_template, request, current_app
from flask_user import roles_required

from ..forms import WatcherControlForm

watcher_blueprint = Blueprint(
    'watchers', __name__, template_folder='templates')


@watcher_blueprint.route('/')
def index():
    return render_template('watcher/index.html')


@watcher_blueprint.route('/stats/')
@watcher_blueprint.route('/stats/<int:watcher_id>')
def stats(watcher_id=None):
    return render_template('watcher/stats.html')


@watcher_blueprint.route('/control', methods=['GET', 'POST'])
@roles_required(['admin'])
def control():
    app = current_app

    form = WatcherControlForm()
    form.update_choices()

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.data['action'] == 'START':
                app.watcher_manager.start(id=form.data['watcherID'])
            elif form.data['action'] == 'STOP':
                app.watcher_manager.stop(id=form.data['watcherID'])
            else:  # RELOAD
                app.watcher_manager.reload(id=form.data['watcherID'])

    return render_template('watcher/control.html', form=form)
