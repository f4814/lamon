""" Collection of functions to retrieve statistics """
from . import db
from .models import User, Event, EventType

def currently_playing(watcher_id=None, game_id=None):
    events = Event.query.\
        filter(Event.type == EventType.USER_JOIN, Event.type == EventType.USER_LEAVE).\
        order_by(Event.time.asc()).all()

    return -2

def number_of_players(watcher_id=None, game_id=None):
    query = User.query

    if watcher_id is not None:
        query = query.filter(User.events.any(Event.watcherID == watcher_id))

    if game_id is not None:
        query = query.filter(User.events.any(Event.gameID == game_id))

    return len(list(query.all()))

def score(game_id=None, user_id=None, timeline=False):
    return 3


def register_stats(app):
    app.jinja_env.globals.update(stats_number_of_players=number_of_players)
    app.jinja_env.globals.update(stats_currently_playing=currently_playing)
    app.jinja_env.globals.update(stats_score=score)
