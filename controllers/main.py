import os
from flask import *
import hashlib
from werkzeug.utils import secure_filename
import MySQLdb
import MySQLdb.cursors

main = Blueprint('main', __name__, template_folder='templates')

#=================For uploading files======================#

UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#==========================================================#

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

@main.route('/album/edit', methods=["GET", "POST"])

def album_edit_route():

    if request.method == "GET" :

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

        return render_template("album_edit.html", photos=photos, albumid=albumid)

    if request.method == "POST" :
        if (request.form.get("op") == "add"):

            album_id = request.form.get("albumid")

            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']

            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')

            if file and allowed_file(file.filename):

                filename, file_type = os.path.splitext(file.filename)
                filename_full = filename + file_type
                file_type_no_dot = file_type[1:]

                m = hashlib.md5(str(album_id) + filename_full)
                hashed_filename = m.hexdigest()
                full_hashed = hashed_filename + file_type
             
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], full_hashed))

                db = connect_to_database()
                cur = db.cursor()
                cur.execute('SELECT MAX(sequencenum) FROM Contain')
                high_sequence = cur.fetchall()
                sequencenum = high_sequence[0]['MAX(sequencenum)']
                if sequencenum is None:
                    sequencenum = 0
                else:
                    sequencenum += 1
                sequencenum = str(sequencenum)
                cur = db.cursor()
                cur.execute("INSERT INTO Photo (picid, format) VALUES ( '" + str(hashed_filename) + "', '" + str(file_type_no_dot) + "');")
                cur = db.cursor()
                cur.execute("INSERT INTO Contain (sequencenum, albumid, picid, caption) VALUES ( '" + sequencenum + "', '" + album_id + "', '" + hashed_filename + "', '');" )
                cur = db.cursor()
                cur.execute("UPDATE Album SET lastupdated=CURRENT_TIMESTAMP WHERE albumid=" + album_id + ";")

                cur = db.cursor()
                cur.execute('SELECT Contain.picid, Photo.format FROM Contain INNER JOIN Photo on Contain.picid=Photo.picid WHERE albumid = ' + album_id + ';')
                results = cur.fetchall()
                photos = []
                for result in results:
                    pair = []
                    pair.append(result['picid'])
                    pair.append(result['format'])
                    photos.append(pair)

                return render_template("album_edit.html", photos=photos, albumid=album_id)
