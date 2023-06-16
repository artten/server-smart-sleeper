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
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "INSERT INTO users (email, password, birthday, gender, height, weight)" \
          " VALUES (%s, %s, %s, %s, %s, %s)"
    vals = (email, password, birthday, gender, height, weight)
    result = mycursor.execute(sql, vals)
    mysql.commit()
    sql = "INSERT INTO alarm_start (email, start_music_sec)" \
          " VALUES (%s, %s)"
    vals = (email, 600)
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '%s, %s, %s, %s);"

    vals = (email, "Sunday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '%s, %s, %s, %s);"

    vals = (email, "Monday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '%s, %s, %s, %s);"

    vals = (email, "Tuesday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '" \
          "%s, %s, %s, %s);"

    vals = (email, "Wednesday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '%s, %s, %s, %s);"

    vals = (email, "Thursday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '%s, %s, %s, %s);"

    vals = (email, "Friday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, '%s, %s, %s, %s);"

    vals = (email, "Saturday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    Util.close_db(mysql)
    if not result:
        return "somthing went wrong"
    return "ok"


@app.route("/add_rating")
def add_ratings():
    email = request.args.get('email')
    rate = request.args.get('rate')
    sleep_id = backend.get_sleep_id_for_rating(email)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    backend.update_alarm_start(float(rate), email)
    sql = "INSERT INTO sleep_rating (email, sleep_id, rate)" \
          " VALUES (%s, %s, %s)"
    vals = (email, sleep_id, rate)
    result = mycursor.execute(sql, vals)
    mysql.commit()
    Util.close_db(mysql)
    if result:
        return "somthing went wrong"
    return "ok"


@app.route("/set_alarm")
def set_alarm():
    email = request.args.get('email')
    day = request.args.get('day')
    action = request.args.get('action')
    hour = request.args.get('hour')
    date = request.args.get('date')
    if date == "":
        date = 0
    if day == "Date":
        day = 0
    if action == "":
        action = 0
    try:
        # today = date.today()
        # sleep_time = datetime.strptime(wake_time, '%H:%M:%S') + timedelta(hours=-8)
        # tomorrow = today + timedelta(1)
        # wake_date = tomorrow
        # sleep_date = today
        # sleep_time = str(sleep_time.time())
        mysql = Util.connect_to_db()
        mycursor = mysql.cursor()

        sql = "INSERT INTO schedule (email, day, action, hour, date)" \
              " VALUES (%s, %s, %s, %s, %s)"
        vals = (email, day, action, hour, date)
        result = mycursor.execute(sql, vals)
        mysql.commit()
        Util.close_db(mysql)
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
            return "ok"
        else:
            return "not ok"
    except Exception as e:
        print(e)
        return "not ok"


@app.route("/add_sleep_stages")
def add_sleep_stages():
    global sleep_id
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
            if start == "done":
                sleep_id = 0
                return "need rating"

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
            backend.calc_sleep_quality(sleep_id)
            return "ok"
        except Exception as e:
            # print(e)
            return "not ok"
    return "not ok no try"


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
