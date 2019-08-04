from datetime import datetime

from ..models import EventType, Event


class Watcher__Events():
    """ Helper functions to emit supported events """

    def start_event(self):
        """ Saves a :attr:`~EventType.WATCHER_START` event """
        self._add_event(Event(type=EventType.WATCHER_START))

    def stop_event(self):
        """ Saves a :attr:`~EventType.WATCHER_STOP` event """
        self._add_event(Event(type=EventType.WATCHER_STOP))

    def connection_lost_event(self):
        """ Saves a :attr:`~EventType.WATCHER_CONNECTION_LOST` event """
        self._add_event(Event(type=EventType.WATCHER_CONNECTION_LOST))

    def connection_reaquired_event(self):
        """ Saves a :attr:`~EventType.WATCHER_CONNECTION_REAQUIRED` event """
        self._add_event(Event(type=EventType.WATCHER_CONNECTION_REAQUIRED))

    def score_event(self, nickname, score):
        """ Save a new score into the database. Emits a
        :attr:`~EventType.USER_SCORE` event.

        :type score: :class:`float`
        :param score: Absolute score of the user

        :type nickname: :class:`str`
        :param nickname: Nickname of user who scored
        """
        user = self._get_user(nickname)
        self._add_event(Event(userID=user.id, gameID=self._model.gameID,
                              type=EventType.USER_SCORE, info=str(score)))

    def join_event(self, nickname):
        """ Save a :attr:`~EventType.USER_JOIN` event

        :type nickname: :class:`str`
        :param nickname: Nickname of user who joined
        """
        user = self._get_user(nickname)
        self._add_event(Event(userID=user.id, gameID=self._model.gameID,
                              type=EventType.USER_JOIN))

    def leave_event(self, nickname):
        """ Save a :attr:`~EventType.USER_LEAVE` event

        :type nickname: :class:`str`
        :param nickname: Nickname of user who left
        """
        user = self._get_user(nickname)
        self._add_event(Event(userID=user.id, gameID=self._model.gameID,
                              type=EventType.USER_LEAVE))

    def die_event(self, nickname):
        """ Save a :attr:`~EventType.USER_LEAVE` event

        :type nickname: :class:`str`
        :param nickname: Nickname of user who scored
        """
        user = self._get_user(nickname)
        self._add_event(Event(userID=user.id, gameID=self._model.gameID,
                              type=EventType.USER_DIE))

    def respawn_event(self, nickname):
        """ Save a :attr:`~EventType.USER_RESPAWN` event

        :type nickname: :class:`str`
        :param nickname: Nickname of user who respawned
        """
        user = self._get_user(nickname)
        self._add_event(Event(userID=user.id, gameID=self._model.gameID,
                              type=EventType.USER_RESPAWN))

    def exception_event(self, exception):
        """ Save a :attr:`~EventType.WATCHER_EXCEPTION` event.

        :type exception: :class:`Exception`
        :param exception: Exception to log
        """
        self._add_event(Event(type=EventType.WATCHER_EXCEPTION,
                              info=str(exception)))

    def _get_user(self, nickname):
        """ Get the :class:`lamon.models.User` with the associated Nickname

        :type nickname: str
        :param nickname: Nickname

        :raises ValueError: When no user with the given nickname is found
        """
        query = self._session.query(User).join(Nickname).\
            filter(Nickname.nick == nickname).\
            filter(Nickname.gameID == self._model.game.id)

        try:
            return query.one()
        except NoResultFound:
            raise ValueError(f'No user with given nickname ({nickname}) found')

    def _add_event(self, event):
        """ Add a event to the database

        :type event: lamon.models.Event
        :param event: Event to add to the database. `event.watcherID` and
            `event.time` are set by this function
        """
        event.watcherID = self._model_id

        if event.time is None:
            event.time = datetime.now()

        self._session.add(event)
        self._session.commit()

        self.logger.debug(str(event))
