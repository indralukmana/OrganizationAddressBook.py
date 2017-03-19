import os
import sqlite3
from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash
from flask.ext import excel

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
def contacts_list():
    db = get_db()

    cur = db.execute(
        'SELECT id, organization, contactPerson, phoneNumber, email, address FROM contacts ORDER BY organization ASC ')
    contacts = cur.fetchall()

    return render_template("contacts_list.html", contacts=contacts)


@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.method == 'POST':
        db.execute('INSERT INTO contacts (organization, contactPerson, phoneNumber, email, address) VALUES (?, ?, ?, ?, ?)',
                   [request.form['organization'], request.form['contactPerson'], request.form['phoneNumber'],
                    request.form['email'], request.form['address']])
        db.commit()
        flash('New contact successfully added')
        return redirect(url_for('contacts_list'))
    elif request.method == 'GET':
        return redirect(url_for('contacts_list'))


@app.route('/remove/<contact_id>')
def remove_contact(contact_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id = ?', [contact_id])
    db.commit()
    flash('Contact has been removed')
    return redirect(url_for('contacts_list'))


@app.route('/edit/<contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.method == 'POST':
        db.execute('UPDATE contacts SET organization=?, contactPerson=?, phoneNumber=?, email=?, address=? WHERE  id=?',
                   [request.form['organization'], request.form['contactPerson'],
                    request.form['phoneNumber'], request.form['email'],
                    request.form['address'], contact_id])
        db.commit()
        flash('Contact successfully edited')
        return redirect(url_for('select_contact', contact_id=contact_id))
    elif request.method == 'GET':
        cur = db.execute(
            'SELECT id, organization, contactPerson, phoneNumber, email, address FROM contacts ORDER BY organization ASC ')
        contacts = cur.fetchall()

        cur = db.execute('SELECT id, organization, contactPerson, phoneNumber, email, address '
                         'FROM contacts '
                         'WHERE id=? ', [contact_id])
        selected_contact = cur.fetchall()

        disabled = ' '
        edit_cancel = 'cancel'

        return render_template('contacts_list.html', contacts=contacts, selected_contact=selected_contact[0], disabled=disabled, edit_cancel=edit_cancel)
    return redirect(url_for('contacts_list'))


@app.route('/select/<contact_id>', methods=['GET'])
def select_contact(contact_id):
    db = get_db()
    if request.method == 'GET':
        cur = db.execute(
            'SELECT id, organization, contactPerson, phoneNumber, email, address FROM contacts ORDER BY organization ASC ')
        contacts = cur.fetchall()

        cur = db.execute('SELECT id, organization, contactPerson, phoneNumber, email, address '
                         'FROM contacts '
                         'WHERE id=? ', [contact_id])
        selected_contact = cur.fetchall()
        return render_template('contacts_list.html', contacts=contacts, selected_contact=selected_contact[0])
    return redirect(url_for('contacts_list'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # if request.form['username'] != app.config['USERNAME']:
        #     error = 'Invalid username'
        # elif request.form['password'] != app.config['PASSWORD']:
        #     error = 'Invalid password'
        # else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('contacts_list'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('contacts_list'))

if __name__ == '__main__':
    app.run()
