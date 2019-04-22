from flask_user import UserMixin
from sqlalchemy import DateTime
from datetime import datetime
from enum import IntEnum, unique, auto

from lamon import db


class User(db.Model, UserMixin):
    """ A User

    :param username: Username to authenticate with lamon
    :param password: Hashed password
    :param nicknames: :class:`Nickname` s of the User
    :param events: Events concerning the user (like scores, joins, etc.)
    :param roles: System roles of the user
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    is_enabled = True

    nicknames = db.relationship('Nickname', back_populates='user')
    events = db.relationship('Event', back_populates='user')
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return self.username


class Event(db.Model):
    """ Events are used log keep a log of things happening. This includes events
    on watched servers (scores, kills), server events (unavailable) and
    watcher events (restarted, started, stopped).

    :param type: An :class:`EventType` specifies how to handle this event
    :param time: Time the event occurred
    :param info: Additional info. Changes with :attr:`type`
    :param watcher: Watcher the event occurred in (If any)
    :param game: Game the event occured in (If any)
    :param user: User connected to the event (If any)
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    time = db.Column(DateTime())
    info = db.Column(db.String)

    watcherID = db.Column(db.Integer, db.ForeignKey('watchers.id'))
    watcher = db.relationship('Watcher', back_populates='events')

    gameID = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game', back_populates='events')

    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='events')

    def __init__(self, type=None, **kwargs):
        super().__init__(type=int(type), **kwargs)

    def __str__(self):
        msg = str(EventType(self.type)) + ": "

        if self.watcherID is not None:
            msg += "Watcher = {}; ".format(str(self.watcher))

        if self.gameID is not None:
            msg += "Game = {}; ".format(str(self.game))

        if self.userID is not None:
            msg += "Gmae = {}; ".format(str(self.game))

        return msg


class Game(db.Model):
    """ A game or gamemode played by the users

    :param name: Name of the game, can be anything
    :param nicknames: Nicknames registered for this game
    :param events: Events in the Game
    :param watchers: Watchers watching the game
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    nicknames = db.relationship('Nickname', back_populates='game')
    events = db.relationship('Event', back_populates='game')
    watchers = db.relationship('Watcher', back_populates='game')

    def __repr__(self):
        return self.name


class Watcher(db.Model):
    """ A Watcher is a process keeping track of one or more gameservers

    :param threadClass: Implementation of the process
    :param config: Configuration values the process needs (like server ip)
    :param events: Events occured in the watcher
    :param game: Game watched by the watcher
    """
    __tablename__ = 'watchers'

    id = db.Column(db.Integer, primary_key=True)
    threadClass = db.Column(db.String)
    config = db.relationship('WatcherConfig', back_populates='watcher')

    events = db.relationship('Event', back_populates='watcher')

    gameID = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game', back_populates='watchers')

    def __repr__(self): return "{} ({})".format(
        self.game, self.config)


class Role(db.Model):
    """ A user role on the system

    :param name: Name of the role
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
        return self.name


class UserRoles(db.Model):
    """ Many-to-many mapper between :class:`User` and :class:`Role` """
    __tabelname__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'roles.id', ondelete='CASCADE'))


class Nickname(db.Model):
    """ The nickname of a user in a game

    :param nick: Nickname
    :param user: Associated user
    :param game: Associated game
    """
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


class WatcherConfig(db.Model):
    """ A key value pair in a :class:`Watcher` configuration

    :param watcher: Associated watcher
    :param key: Key
    :param value: Value
    """
    __tablename__ = 'watcherconfig'

    id = db.Column(db.Integer, primary_key=True)

    watcherID = db.Column(db.Integer, db.ForeignKey('watchers.id'))
    watcher = db.relationship('Watcher', back_populates='config')

    key = db.Column(db.String)
    value = db.Column(db.String)

    def __repr__(self):
        return self.key + ": " + self.value


@unique
class EventType(IntEnum):
    """ A Type of event used in :attr:`~Event.type`

    **Watcher related events**. :attr:`Event.watcherID` has to be set

    :param WATCHER_RELOAD: Watcher reloaded it's config.
    :param WATCHER_START: Watcher started
    :param WATCHER_STOP: Watcher stopped
    :param WATCHER_CONNECTION_LOST: Watcher lost connection
    :param WATCHER_CONNECTION_REAQUIRED: Watcher got connection back

    **User related events**. :attr:`Event.userID`, :attr:`Event.watcherID` and
    :attr:`Event.gameID` have to be set.

    :param USER_SCORE: User score. :attr:`Event.info` is the absolute score.
    :param USER_JOIN: User joined a game.
    :param USER_LEAVE: User left a game.
    :param USER_DIE: User died in game
    :param USER_RESPAWN: User respawned after death
    """
    WATCHER_RELOAD = 1000
    WATCHER_START = 1001
    WATCHER_STOP = 1002
    WATCHER_CONNECTION_LOST = 1003
    WATCHER_CONNECTION_REAQUIRED = 1004

    USER_SCORE = 2000
    USER_JOIN = 2001
    USER_LEAVE = 2002
    USER_DIE = 2003
    USER_RESPAWN = 2004
