from time import sleep, time
from random import randrange, choice

from lamon.watcher import Watcher
from lamon.models import Game, User, Nickname


class FakeWatcher(Watcher):
    """ Testing watcher. Does nothing """

    config_keys = {}

    def __new__(cls, *args, **kwargs):
        inst = object.__new__(cls)
        if not 'config_keys' in kwargs:
            kwargs['config_keys'] = {
                'key1': {'type': str, 'required': True},
                'key2': {'type': str, 'required': False},
                'key3': {'type': int, 'required': True}}

        inst.config_keys = kwargs['config_keys']
        return inst

    def __init__(self, **kwargs):
        super().__init__(__name__, kwargs['session'], kwargs['model_id'])

    def runner(self):
        while getattr(self, 'shutdown', True):
            pass


class ValueWatcher(Watcher):
    """ Insert random testing values """

    def __init__(self, **kwargs):
        super().__init__(__name__, **kwargs)

    def runner(self):
        while getattr(self, 'shutdown', True):
            game = choice(self._session.query(Game).all())
            self._model.game = game
            self._session.commit()

            new_round = time() + (5 * 60)

            self.start_event()
            users = self._session.query(User).\
                filter(User.nicknames.any(Nickname.game == game)).all()
            for user in users:
                setattr(user, 'nickname',
                        self._session.query(Nickname).
                        filter(Nickname.user == user, Nickname.game == game)
                            .one().nick)
                self.join_event(user.nickname)

            while new_round > time():
                num_user = randrange(len(users))
                self.score_event(users[num_user].nickname, randrange(100))
                sleep(5)

            for user in users:
                self.leave_event(user.nickname)
