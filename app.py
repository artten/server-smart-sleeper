from flask import request
from flask import Flask
from datetime import date, timedelta, datetime
import Util
import backend
import mysql
import SRAI

app = Flask(__name__)

sleep_id = 0
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
    mysql = Util.connect_to_db()
    result = Util.execute_sql(mysql, "select * from users where email='" + email + "'")
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
    return backend.add_user(email, password, birthday, gender, height, weight)


@app.route("/add_rating")
def add_ratings():
    email = request.args.get('email')
    rate = request.args.get('rate')
    return backend.add_rating(email,rate)


@app.route("/set_alarm")
def set_alarm():
    email = request.args.get('email')
    day = request.args.get('day')
    action = request.args.get('action')
    hour = request.args.get('hour')
    date = request.args.get('date')
    return backend.add_alarm(date, day, action, email, hour)


@app.route("/add_sleep")
def add_sleep():
    email = request.args.get('email')
    wake_date = request.args.get('wake_date')
    quality = request.args.get('quality')
    backend.add_sleep(email, wake_date, quality)


@app.route("/add_sleep_stages")
def add_sleep_stages():
    start = request.args.get('start')
    end = request.args.get('end')
    sleep_type = request.args.get('sleep_type')
    backend.add_sleep_stages(start, end, sleep_type)


@app.route("/get_alarm")
def get_alarm():
    email = request.args.get('email')
    answer = backend.get_wake_time(email)
    wake_time = answer
    if answer == 'not':
        return 'not'
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select start_music_sec from alarm_start where email = '" + email + "'"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    print("here")
    print(str(result[-1][0]))
    answer = answer + "." + str(result[-1][0])
    if not result:
        return "somthing went wrong"
    # answer = answer + backend.get_waking_time(wake_time)
    answer = answer + "." + backend.get_sleeping_time(email, wake_time) + ","
    return answer


@app.route("/get_all_alarms")
def get_all_alarms():
    email = request.args.get('email')
    return backend.get_all_futere_alarms(email)


@app.route("/get_all_sleeps")
def get_all_sleeps():
    email = request.args.get('email')
    return backend.get_all_qulity_of_sleep(email)


@app.route("/get_setting")
def get_setting():
    email = request.args.get('email')
    return backend.get_settings(email)


@app.route("/set_setting")
def set_setting():
    email = request.args.get('email')
    birthday = request.args.get('birthday')
    gender = request.args.get('gender')
    height = request.args.get('height')
    weight = request.args.get('weight')
    backend.update_settings(email, birthday, gender, height, weight)
    return "ok"


@app.route("/get_when_to_wake_up")
def get_when_to_wake_up():
    email = request.args.get('email')
    sleep_time = request.args.get('sleep_time')
    return backend.get_when_to_wake_up(email, sleep_time) + ","
