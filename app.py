from flask import request
from flask import Flask
from datetime import date, timedelta, datetime
import Util
import backend
import mysql

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


@app.route("/set_alarm")
def set_alarm():
    email = request.args.get('email')
    wake_time = request.args.get('wake_time')
    try:
        today = date.today()
        sleep_time = datetime.strptime(wake_time, '%H:%M:%S') + timedelta(hours=-8)
        tomorrow = today + timedelta(1)
        wake_date = tomorrow
        sleep_date = today
        sleep_time = str(sleep_time.time())
        mysql = Util.connect_to_db()
        mycursor = mysql.cursor()

        sql = "INSERT INTO alarms (email, wake_date, wake_time, sleep_date, sleep_time)" \
              " VALUES (%s, %s, %s, %s, %s)"
        vals = (email, wake_date, wake_time, sleep_date, sleep_time)
        result = mycursor.execute(sql, vals)
        mysql.commit()
        Util.close_db(mysql)
        print(result)
        return "ok"

    except:
        return "somthing went wrong"


@app.route("/add_sleep")
def add_sleep():
    global sleep_id
    try:
        email = request.args.get('email')
        wake_date = request.args.get('wake_date')
        quality = request.args.get('quality')
        mydb = mysql.connector.connect(
        host="localhost",
        user="artiom",
        password="password",
        database="smart_sleeper"
        )
        if not backend.check_if_sleep_registered(int(wake_date)):
            mycursor = mydb.cursor()
            mycursor.execute("select start_music_sec from alarm_start where email = '" + email + "';")
            result = mycursor.fetchall()
            min_before = result[0][0]/60

            wake_date = datetime.fromtimestamp(float(wake_date) / 1000.0)
            wake_date = wake_date.strftime("%Y-%m-%d")

            sql = "INSERT INTO sleeps (email, date, quality, min_before)" \
                  " VALUES (%s, %s, %s, %s)"
            vals = [(email, wake_date, quality, min_before)]
            mycursor.executemany(sql, vals)

            mydb.commit()

            mycursor.execute("select max(sleep) from sleeps where email = '" + email + "';")
            result = mycursor.fetchall()
            mycursor.close()
            sleep_id = result[0][0]
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(sleep_id)
            return "ok"
        else:
            return "not ok"
    except Exception as e:
        print(e)
        return "not ok"

@app.route("/add_sleep_stages")
def add_sleep_stages():
    print(sleep_id)
    if sleep_id != 0:
        try:
            sleep = sleep_id
            start = request.args.get('start')
            end = request.args.get('end')
            sleep_type = request.args.get('sleep_type')
            mydb = mysql.connector.connect(
            host="localhost",
            user="artiom",
            password="password",
            database="smart_sleeper"
            )

            mycursor = mydb.cursor()
            # if start == "done":
            #     sleep_id = 0
            #     return "ok"

            start = datetime.fromtimestamp(float(start) / 1000.0)
            start = start.strftime("%Y-%m-%d %H:%M:%S")

            end = datetime.fromtimestamp(float(end) / 1000.0)
            end = end.strftime("%Y-%m-%d %H:%M:%S")

            sql = "INSERT INTO sleep_stages (sleep, start, end, type)" \
                  " VALUES (%s, %s, %s, %s)"
            vals = [(sleep, start, end, sleep_type)]
            mycursor.executemany(sql, vals)

            mydb.commit()
            mycursor.close()
            return "ok"
        except Exception as e:
            # print(e)
            return "not ok"
    return "not ok no try"
