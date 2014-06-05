# all the imports
from __future__ import with_statement
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash

# configuration
DATABASE = '/tmp/beacon_log.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#for reguluar template which refreshes, just show the
#most recent few
SHOW_MAX=50

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_latest():
    cur = g.db.execute('select * from entries order by date_str DESC limit %s'%SHOW_MAX)
    entries = [dict(id=row[0], uuid=row[1], major=row[2], minor=row[3], rssi=row[4], date_str=row[5]) for row in cur.fetchall()]  
    return render_template('log.html', entries=entries)

@app.route('/all')
def show_all():
    cur = g.db.execute('select * from entries order by date_str DESC')
    entries = [dict(id=row[0], uuid=row[1], major=row[2], minor=row[3], rssi=row[4], date_str=row[5]) for row in cur.fetchall()]
    return render_template('log_all.html', entries=entries)


@app.route('/submit', methods=['POST'])
def submit_entry():
    g.db.execute('insert into entries (uuid, major,minor,rssi,date_str) values (?, ?, ?, ?, ?)',
            [request.form['uuid'], request.form['major'], request.form['minor'], request.form['rssi'], request.form['date_str']])
    g.db.commit()
    return 'this is ok'

if __name__ == '__main__':
    app.run()
