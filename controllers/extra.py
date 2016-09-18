from flask import *
import MySQLdb
import MySQLdb.cursors

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def main_route():
    return render_template('index.html')

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
