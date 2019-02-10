from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from sqlalchemy import DateTime
from datetime import datetime

from lamon import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

    nicknames = db.relationship('Nickname', back_populates='user')
    watchers = db.relationship('UserWatcher', back_populates='user')
    scores = db.relationship('Score', back_populates='user')
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

class UserRoles(db.Model):
    __tabelname__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class Nickname(db.Model):
    __tablename__ = 'nicknames'

    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String)

    userID = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', back_populates='nicknames')

    gameID = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='CASCADE'))
    game = db.relationship('Game', back_populates='nicknames')

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer)
    time = db.Column(DateTime())

    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='scores')

    gameID = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game', back_populates='scores')

    def __init__(self, points, time=datetime.now(), game=None, user=None):
        self.points = points
        self.time = time
        self.game = game
        self.user = user

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    scores = db.relationship('Score', back_populates='game')
    nicknames = db.relationship('Nickname', back_populates='game')
    watchers = db.relationship('GameWatcher', back_populates='game')

class GameWatcher(db.Model):
    __tablename__ = 'gamewatchers'

    id = db.Column(db.Integer, primary_key=True)
    gameID = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game', back_populates='watchers')
    state = db.Column(db.String)
    threadClass = db.Column(db.String)
    config = db.Column(db.String)

class UserWatcher(db.Model):
    __tablename__ = 'userwatchers'

    id = db.Column(db.Integer, primary_key=True)

    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='watchers')
    state = db.Column(db.String)
    threadClass = db.Column(db.String)
    config = db.Column(db.String)
