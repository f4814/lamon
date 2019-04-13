from flask import Blueprint, render_template
from flask_user import login_required

user_blueprint = Blueprint('users', __name__, template_folder='templates')

@user_blueprint.route('/')
def index():
    return render_template('user/index.html')


@user_blueprint.route('/stats')
@user_blueprint.route('/stats/<string:username>')
@login_required
def stats(username=None):
    return render_template('user/stats.html')
