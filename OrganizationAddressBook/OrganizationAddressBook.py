import os
import sqlite3
from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'OrganizationAddressBook.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('OAB_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Database initialized.')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def hello_world():
    db = get_db()
    cur = db.execute('SELECT id, organization, contactPerson, phoneNumber, email, address FROM contacts ORDER BY id DESC ')
    contacts = cur.fetchall()
    return render_template("index.html", contacts=contacts)


if __name__ == '__main__':
    app.run()
