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


    #Get the pic id of all the images in the databse with the album id in order of seq num
    #Then select the next and prev pic compared to the photos seq number
    cur.execute("SELECT picid FROM Contain WHERE albumid='" + str(data['albumid']) + "' ORDER BY sequencenum ASC")
    results = cur.fetchall()
    for index in range(len(results)):
        if results[index]['picid'] == data['current'] and index != len(results) - 1:
            data['next'] = results[index + 1]['picid']
        if results[index]['picid'] == data['current'] and index != 0:
            data['prev'] = results[index - 1]['picid']

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

@main.route('/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():
    #Connect to database
    db = connect_to_database()
    cur = db.cursor()
    #Get username from url
    username = request.args.get('username')
    #Get Post data if form was submitted
    opcode = request.form.get("op")

    #Check if Opcode has a value
    if opcode == "delete":
        #Delete the album
        albumid = request.form.get("albumid")
        #Get pics to delete from album
        cur.execute("SELECT picid FROM Contain WHERE albumid = '" + albumid + "';")
        results = cur.fetchall()
        for result in results:
            #Get photo format
            cur.execute("SELECT format FROM Photo WHERE picid='" + result['picid'] + "';")
            photoFormat = cur.fetchone()
            #Delete photo from file
            os.remove("static/images/" + result['picid'] + "." + photoFormat['format'])
            #Delete photo from database
            cur.execute("DELETE FROM Contain WHERE picid='" + result['picid'] + "';")
            cur.execute("DELETE FROM Photo WHERE picid='" + result['picid'] + "';")
        #Delete album
        cur.execute("DELETE FROM Album WHERE albumid='" + albumid + "';")

    if opcode == "add":
        #Add new album
        title = request.form.get("title")
        cur.execute("INSERT INTO Album (title, username) VALUES ('" + title + "', '" + username + "');")


    cur.execute("SELECT albumid, title FROM Album WHERE username = '" + username + "';")
    results = cur.fetchall()
    albums = []
    for result in results:
        albums.append({"title":result['title'], "id":result['albumid']})

    return render_template("albums_edit.html", albums = albums, username = username)

@main.route('/album/edit', methods=["GET", "POST"])
def album_edit_route():

    #Connect to database
    db = connect_to_database()
    cur = db.cursor()
    albumid = request.args.get('albumid')

    #Check if user sent data via post method
    if request.method == "POST" :
        #They are editing the album so get the info that they sent in the post
        albumid = request.form.get('albumid')
        db = connect_to_database()
        cur = db.cursor()

        if (request.form.get("op") == "add"):

            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']

            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')

            #grabs information for valid file names
            if file and allowed_file(file.filename):

                filename, file_type = os.path.splitext(file.filename)
                filename_full = filename + file_type
                file_type_no_dot = file_type[1:]

                m = hashlib.md5(str(albumid) + filename_full)
                hashed_filename = m.hexdigest()
                full_hashed = hashed_filename + file_type

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], full_hashed))


                cur = db.cursor()
                cur.execute('SELECT MAX(sequencenum) FROM Contain')
                high_sequence = cur.fetchall()
                sequencenum = high_sequence[0]['MAX(sequencenum)']

                #error checks for if no info in database
                if sequencenum is None:
                    sequencenum = 0
                else:
                    sequencenum += 1

                #updates database for Photo, Contain, and Album's lastupdated
                sequencenum = str(sequencenum)
                cur = db.cursor()
                cur.execute("INSERT INTO Photo (picid, format) VALUES ( '" + str(hashed_filename) + "', '" + str(file_type_no_dot) + "');")
                cur = db.cursor()
                cur.execute("INSERT INTO Contain (sequencenum, albumid, picid, caption) VALUES ( '" + sequencenum + "', '" + albumid + "', '" + hashed_filename + "', '');" )
                cur = db.cursor()
                cur.execute("UPDATE Album SET lastupdated=CURRENT_TIMESTAMP WHERE albumid=" + albumid + ";")


        #If opcode was delete then delete the image
        if request.form.get('op') == "delete":
            picid = str(request.form['picid'])
            #Get pics format
            cur.execute("SELECT format From Photo WHERE picid='" + picid + "';")
            photoFormat = cur.fetchone()
            #Delete the pic from the database
            cur.execute("DELETE FROM Contain WHERE albumid='" + albumid + "' AND picid=" + "'" + picid + "';")
            cur.execute("DELETE FROM Photo WHERE picid='" + picid + "';")
            #Remove the photo from server
            os.remove("static/images/" + picid + "." + photoFormat['format'])

    #cursor to database and returns template
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
