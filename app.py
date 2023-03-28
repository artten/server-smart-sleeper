from flask import request
from flask import Flask
import Util

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test")
def test():
    mysql = Util.connect_to_db()
    result = Util.execute_sql(mysql, "select * from test")
    Util.close_db(mysql)
    return result


@app.route("/login")
def login():
    email = request.args.get('email')
    password = request.args.get('password')
    mysql = Util.connect_to_db()
    result = Util.execute_sql(mysql, "select * from users where email='" + email + "' and password='" + password + "'")
    Util.close_db(mysql)
    if not result:
        return "no user"
    return "ok"


@app.route("/register")
def register():
    email = request.args.get('email')
    password = request.args.get('password')
    birthday = request.args.get('birthday')
    gender = request.args.get('gender')
    height = request.args.get('height')
    weight = request.args.get('weight')
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "INSERT INTO users (email, password, birthday, gender, height, weight)" \
          " VALUES (%s, %s, %s, %s, %s, %s)"
    vals = (email, password, birthday, gender, height, weight)
    result = mycursor.execute(sql, vals)
    mysql.commit()
    Util.close_db(mysql)
    print(result)
    if not result:
        return "somthing went wrong"
    return "ok"


@app.route("/add_rating")
def add_ratings():
    email = request.args.get('email')
    rate = request.args.get('rate')
    sleep_id = request.args.get('sleep_id')
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "INSERT INTO sleep_rating (email, sleep_id, rate)" \
          " VALUES (%s, %s, %s)"
    vals = (email, sleep_id, rate)
    result = mycursor.execute(sql, vals)
    mysql.commit()
    Util.close_db(mysql)
    print(result)
    if not result:
        return "somthing went wrong"
    return "ok"

