:tocdepth: 2

Introduction
############

Installation
============
The easiest way to install lamon is via pip:

.. code-block:: bash

    pip install lamon


Getting Started
===============
In order to use lamon, you have to create a configuration file. To use the
default one just copy `config.toml.example` to `config.toml` and start
lamon in the same directory. This will create a sqlite3 database named `lamon.db`.

Lamon provides a simple cli wrapper, which should be sufficient in most cases.

.. code-block:: bash

    lamon --host 127.0.0.1 --port 5000 --config config.toml

Configuration
=============
The configuration file (``./config.toml``) defines uses four seperate blocks:

.. code-block:: ini

    [app]
    # stuff

Every key here is converted to uppercase and (with it's corresponding value)
appended to the Flask config.

You should configure a `secret_key`. This is used to encrypt client sessions.
To generate a key you can use this in your shell:

.. code-block:: bash

    python -c 'import os; print(os.urandom(16))'

.. code-block:: ini

    [database]
    database_uri = ''
    secret_key = 'secret'

* ``database_uri``: A sqlalchemy compatible database url. (E.g
  ``sqlite:///test.db`` ``postgresql://user:pass@host/database``)
* ``secret_key``: Secret Key used by sqlalchemy. Should be some long, random string

.. code-block:: ini

    [watcher]
    # stuff

Reserved for future use

.. code-block:: ini

    [logging]
    # stuff

This section is used to configure pythons logging system via
:meth:`logging.config.dictConfig`. And uses the same
`format <https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema>`_

Lamon provides some defaults. So touching this section should (hopefully) be
unneccessary:

.. code-block:: ini

    [logging]
    version = 1

    [logging.root]
    level = "INFO"
    handlers = [ "console",]

    [logging.loggers."lamon.db"]
    level = "WARNING"

    [logging.loggers."flask.app.watcher_manager"]
    level = "WARNING"

    [logging.loggers."flask.app.requests"]
    level = "WARNING"

    [logging.formatters.default]
    format = "%(name)s - %(levelname)s - %(message)s"

    [logging.handlers.console]
    class = "logging.StreamHandler"
    stream = "ext://sys.stdout"
    formatter = "default"

* **Handlers**: By default there is one handler named ``console`` which logs
  everyting to ``sys.stdout`` using the ``default`` formatter.

* **Formatters**: ``'format': '%(name)s - %(levelname)s - %(message)s'``

* **Loggers**:

  * *root*: The ``root`` logger defaults to ``level = logging.INFO``
  * *flask.app*: Everything flask related is logged under this logger.

    * *flask.app.watcher_manager*: Flasks watcher manager logs.
          (Default level: ``logging.WARNING``)
    * *lask.app.requests*: Requests are logged here with
        ``level = logging.DEBUG`` (Default level: ``logging.WARNING``)

  * *lamon*: Other lamon stuff is logged here

    * *lamon.db*: Database related logs (Default level: ``logging.WARNING``)
    * *lamon.watcher*: Watcher logs


Concepts
========

**Games**

**Managers**


Managing Watchers
=================
