import re

from ..models import Event


class LogMixin():
    """ Provide support for parsing logfiles to a watcher.

    This mixin expects the watcher to have a parse attribute when it is created.
    This dict describes how to handle log messages. Each key is a regular-expression
    which is matched against the message. The value is a callable.


    Example:

    .. code-block:: python

        log_parser = {
            'User (\c*) scored: (\c*)': lambda e: self.score_event(e[1], int(e[2]))
        }
    """

    def __init__(self):
        self.logger.debug('Compiling regular expressions')
        for expr, attrs in self.log_parser.items():
            self._compiled[re.compile(expr)] = attrs

    def parse(self, msg):
        for expr, call in self._compiled.items():
            match = re.match(expr, msg)

            if match is None:
                continue

            call(match)
