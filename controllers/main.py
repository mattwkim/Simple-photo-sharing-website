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
    cur.execute("SELECT title, albumid FROM Album WHERE username='" + username + "'")
    results = cur.fetchall()
    albums = []
    ids = []
    for result in results:
        albums.append(result['title'])
        ids.append(result['albumid'])
    return render_template("albums.html", usernamealbums = albums, thealbumids = ids, username = username)
@main.route('/pic')
def pic_route():
    data = {
        'current':request.args.get('picid'),
        'current_format':"",
        'next':"",
        'prev':"",
        'albumid':""}

    #Connect to database
    db = connect_to_database()
    cur = db.cursor()

    #Get pics sequence number and format
    cur.execute("SELECT sequencenum, albumid FROM Contain WHERE picid='" + str(data['current']) + "'")
    result = cur.fetchone()
    pic_seq = result['sequencenum']
    data['albumid'] = result['albumid']

    #Get pics format
    cur.execute("SELECT format FROM Photo WHERE picid='" + str(data['current']) + "'")
    result = cur.fetchone()
    data['current_format'] = result['format']

    #Get the pic id of the image one less of the sequence number; Make sure they have same album id
    cur.execute("SELECT picid FROM Contain WHERE sequencenum='" + str(pic_seq - 1) + "' AND albumid='" + str(data['albumid']) + "'")
    result = cur.fetchone()
    if result:
        data['prev'] = result['picid'];

    #Get the pic id of the image one less of the sequence number; Make sure they have same album id
    cur.execute("SELECT picid FROM Contain WHERE sequencenum='" + str(pic_seq + 1) + "' AND albumid='" + str(data['albumid']) + "'")
    result = cur.fetchone()
    if result:
        data['next'] = result['picid'];

    return render_template("pic.html", data = data)

@main.route('/album')
def album_route():
	albumid = request.args.get('albumid')
	db = connect_to_database()
	cur = db.cursor()
	cur.execute('SELECT Contain.picid, Photo.format FROM Contain INNER JOIN Photo on Contain.picid=Photo.picid WHERE albumid = ' + albumid + ';')
	results = cur.fetchall()
	photos = []
	for result in results:

		pair = []
		pair.append(result['picid'])
		pair.append(result['format'])

		photos.append(pair)
	return render_template("album.html", photos = photos)
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