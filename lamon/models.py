from flask_user import UserMixin
from sqlalchemy import DateTime
from datetime import datetime

from lamon import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    is_enabled = True

    nicknames = db.relationship('Nickname', back_populates='user')
    watchers = db.relationship('Watcher', back_populates='user')
    scores = db.relationship('Score', back_populates='user')
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return self.username


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
        return self.name


class UserRoles(db.Model):
    __tabelname__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'roles.id', ondelete='CASCADE'))


class Nickname(db.Model):
    __tablename__ = 'nicknames'

    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String)

    userID = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    user = db.relationship('User', back_populates='nicknames')

    gameID = db.Column(db.Integer, db.ForeignKey(
        'games.id', ondelete='CASCADE'))
    game = db.relationship('Game', back_populates='nicknames')

    def __repr__(self):
        r = "{} is {} in {}"
        return r.format(self.user, self.nick, self.game)


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer)
    time = db.Column(DateTime())

    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='scores')

    nicknameID = db.Column(db.Integer, db.ForeignKey('nicknames.id'))

    gameID = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game', back_populates='scores')

    def __init__(self, points, time=None, game=None, user=None, nick=None):
        self.points = points

        if time:
            self.time = time
        else:
            self.time = datetime.Now()

        if game:
            self.game = game
            self.gameID = game.id

        if user:
            self.user = user
            self.userID = user.id

        if nick:
            self.nicknameID = nick.id

    def __repr__(self):
        r = "{} points at {} in {}"
        return r.format(self.points, self.time, self.game)


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    scores = db.relationship('Score', back_populates='game')
    nicknames = db.relationship('Nickname', back_populates='game')
    watchers = db.relationship('Watcher', back_populates='game')

    def __repr__(self):
        return self.name


class Watcher(db.Model):
    __tablename__ = 'watchers'

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String)  # Can be 'RUNNING', 'STOPPED', 'STOPPING'
    threadClass = db.Column(db.String)
    config = db.relationship('WatcherConfig')

    # Gamewatcher
    gameID = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game', back_populates='watchers')

    # Userwatcher
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='watchers')

    def __repr__(self): return "{} [{}], {} ({})".format(
        self.game, self.state, self.user, self.config)


class WatcherConfig(db.Model):
    __tablename__ = 'watcherconfig'

    id = db.Column(db.Integer, primary_key=True)
    watcherID = db.Column(db.Integer, db.ForeignKey('watchers.id'))
    key = db.Column(db.String)
    value = db.Column(db.String)

    def __repr__(self):
        return self.key + ": " + self.value
