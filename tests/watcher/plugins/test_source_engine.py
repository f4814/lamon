from unittest.mock import MagicMock
from sqlalchemy.orm import scoped_session, sessionmaker

from lamon import db
from lamon.models import WatcherConfig
from lamon.watcher.plugin.source_engine import SourceEngineWatcher

class TestSourceEngine():
    """ Test source engine watcher """

    # def setUp(self):
    #     """ Set up a source engine watcher with a mock connection """
    #     super().setUp(threadClass='lamon.watcher.plugin.source_engine.SourceEngineWatcher')
    #
    #     self.watcher_model.config.append(
    #         WatcherConfig(key='address', value='localhost'))
    #     self.watcher_model.config.append(
    #         WatcherConfig(key='port', value='12345'))
    #     self.watcher_model.config.append(
    #         WatcherConfig(key='timeout', value='3'))
    #     self.watcher_model.config.append(
    #         WatcherConfig(key='app_id', value='1'))
    #
    #     db.session.commit()
    #
    #     session = scoped_session(sessionmaker(bin=db.engine))
    #
    #     mock = MagicMock()
    #
    #     self.watcher = SourceEngineWatcher(session=session,
    #                                        model_id=self.watcher_model.id)
