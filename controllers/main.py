from flask import *
import MySQLdb
import MySQLdb.cursors

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def main_route():
    db = connect_to_database()
    cur = db.cursor()
    cur.execute('SELECT username FROM User')
    results = cur.fetchall()
    usernames = []
    for result in results:
        usernames.append(result['username'])
    return render_template("index.html", usernames = usernames)

@main.route('/albums')
def albums_route():
    db = connect_to_database()
    cur = db.cursor()
    username = str(request.args.get('username'))
    cur.execute('SELECT username, title, albumid FROM Album WHERE username="' + username + '"')
    results = cur.fetchall()
    albums = []
    ids = []
    for result in results:
        albums.append(result['title'])
        ids.append(result['albumid'])
    return render_template("albums.html", usernamealbums = albums, thealbumids = ids, username = username)

def connect_to_database():
  options = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'root',
    'db': 'groupXXp1',
    'cursorclass' : MySQLdb.cursors.DictCursor
  }
  db = MySQLdb.connect(**options)
  db.autocommit(True)
  return db

