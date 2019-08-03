from flask import Blueprint, render_template
from flask_user import login_required
from sqlalchemy.orm.exc import NoResultFound

from ..models import User, Nickname

user_blueprint = Blueprint('users', __name__, template_folder='templates')

@user_blueprint.route('/')
def index():
    users = User.query.all()
    return render_template('user/index.html', users=list(users))

@user_blueprint.route('/<int:user_id>')
def index_one(user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
    except NoResultFound:
        abort(404)

    nicknames = Nickname.query.filter(Nickname.user == user).all()
    return render_template('user/index_one.html', user=user, nicknames=nicknames)
