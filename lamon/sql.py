"""
Convenience options for interacting with the database
"""
import sqlite3
import re

def regexp(expr, item):
    """ Custom sqlite regex function """
    reg = re.compile(expr)
    return reg.search(item) is not None

def initDatabase(cursor):
    """
    Create all Tables if they don't exist
    """
    query = """
        SELECT name FROM sqlite_master WHERE type='table'
        """

    createTables = """
        CREATE TABLE player (
            name TEXT NOT NULL,
            PRIMARY KEY(name));

        CREATE TABLE scoreUpdate (
            points INTEGER,
            time TEXT,
            gameName TEXT,
            playerName TEXT,
            FOREIGN KEY(playerName) REFERENCES player(name));

        CREATE TABLE nick (
            gameName TEXT,
            nick TEXT,
            playerName TEXT,
            FOREIGN KEY(playerName) REFERENCES player(name));

        CREATE TABLE inGame (
            playerName TEXT,
            gameName TEXT,
            time INTEGER,
            timespan INTEGER,
            FOREIGN KEY(playerName) REFERENCES player(name));
        """
    if not cursor.execute(query).fetchone():
        cursor.executescript(createTables)

    cursor.connection.create_function("REGEXP", 2, regexp)

    cursor.connection.commit()
    cursor.close()
