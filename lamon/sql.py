"""
Convenience options for interacting with the database
"""
import sqlite3

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
            time INTEGER,
            gameName TEXT,
            playerName TEXT,
            FOREIGN KEY(playerName) REFERENCES player(name));

        CREATE TABLE identity (
            gameName TEXT,
            nick TEXT,
            playerName TEXT,
            FOREIGN KEY(playerName) REFERENCES player(name));
        """
    if not cursor.execute(query).fetchone():
        cursor.executescript(createTables)

    cursor.connection.commit()
    cursor.close()
