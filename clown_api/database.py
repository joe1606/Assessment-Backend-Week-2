"""This file contains methods for communicating with the database."""

from psycopg2 import connect
from psycopg2._psycopg import connection
from psycopg2.extras import RealDictCursor
import psycopg2.extras

def get_db_connection() -> connection:
    """Returns a connection to the database; all rows are returned as dicts."""
    return connect(
        dbname="clown",
        host="localhost",
        port=5432,
        cursor_factory=RealDictCursor
    )


def get_cursor(conn: connection):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return cursor
