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
    result = Util.execute_sql(mysql, "select * from test where name='" + email + "' and age='" + password + "'")
    Util.close_db(mysql)
    if not result:
        return "no user"
    return "ok"

