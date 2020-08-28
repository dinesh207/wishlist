import sqlite3
import json
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.execute("PRAGMA foreign_keys=ON")
        g.db.row_factory = dict_factory

    return g.db


def init_db():
    db = get_db()
    with current_app.open_resource('./db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if isinstance(row[idx], str):
            try:
                obj = json.loads(row[idx])
                d[col[0]] = obj
            except ValueError as e:
                d[col[0]] = row[idx]
        else:
            d[col[0]] = row[idx]
    return d
