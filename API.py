import flask
from flask import Flask
import Util

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test")
def test():
    mysql = Util.connect_to_db()
    mysql.execute("select * from test")
    Util.close_db(mysql)

