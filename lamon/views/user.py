from flask import Blueprint, render_template
from flask_user import login_required

user_blueprint = Blueprint('current', __name__, template_folder='templates')

@user_blueprint.route('/stats')
@login_required
def user_profile():
    return render_template('user/stats.html')
