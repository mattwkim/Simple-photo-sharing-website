from flask import *
import MySQLdb
import MySQLdb.cursors

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def main_route():
    return render_template('index.html')

<<<<<<< HEAD
def connect_to_database():
  options = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'root',
    'db': 'test_db',
    'cursorclass' : MySQLdb.cursors.DictCursor
  }
  db = MySQLdb.connect(**options)
  db.autocommit(True)
  return db

@main.route('/hello')
def test_route():
  db = connect_to_database()
  cur = db.cursor()
  cur.execute('SELECT id, name FROM test_tbl')
  results = cur.fetchall()
  return_string = ''
  for result in results:
    return_string += str(result['id']) + ' ' + str(result['name']) + '\n'
  return return_string

=======
@main.route('/test_database')
def test_route():
  db = connect_to_database()
  cur = db.cursor()
  cur.execute('SELECT username FROM User')
  results = cur.fetchall()
  return_string = ''
  for result in results:
    return_string += str(result['username']) + '\n'
  return return_string
>>>>>>> 4bd8490a0b5845bfdd32211672b375f1de2a1755
