from datetime import timedelta
import mysql.connector
import Util
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from SRAI import *
from datetime import date
import datetime



def get_when_to_start_sleep(wake_up_time):
    # d = '2023-11-24 09:30:00'
    #
    # # 👇️ convert string to datetime object
    # dt = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
    result = wake_up_time + timedelta(hours=-8) # TODO add ai
    return result


def get_when_to_start_music(wake_up_time):
    result = wake_up_time + timedelta(minutes=-10)  # TODO add ai
    return result


def get_users_from_db():
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute("select email, birthday, gender, height, weight from users;")
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    arr = np.array(result)

    count = 0
    for i in arr:
        date = i[1]
        arr[count][1] = (date - datetime.date(1900, 1, 1)).days
        count += 1

    mycursor.close()

    return arr


def get_reviews_from_db():
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute("select birthday, gender, height, weight from users;")
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    arr = np.array(result)

    count = 0
    for i in arr:
        date = i[0]
        arr[count][0] = (date - datetime.date(1900, 1, 1)).days
        count += 1

    mycursor.close()

    return arr


def get_sleep_from_db():
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute("SELECT s.sleep, s.email, s.quality,time_to_sec((SELECT start FROM sleep_stages WHERE sleep = "
                     "s.sleep ORDER BY start ASC LIMIT 1))/60 AS start, time_to_sec((SELECT end FROM sleep_stages"
                     " WHERE sleep = s.sleep ORDER BY end DESC LIMIT 1))/60 as end FROM sleeps AS s;")
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    arr = np.array(result)
    count = 0
    for i in arr:
        if not i[3] or not i[4]:
            arr = np.delete(arr, count, 0)
        else:
            arr[count][2] = float(i[2])
            arr[count][3] = int(i[3])
            arr[count][4] = int(i[4])
            count += 1

    mycursor.close()

    return arr


def get_pred(arr):
    mean_user_rating = np.mean(arr, axis=1).reshape(-1, 1)
    ratings_diff = (arr - mean_user_rating)
    user_similarity = 1 - pairwise_distances(ratings_diff, metric='cosine')
    pred = mean_user_rating + user_similarity.dot(ratings_diff) / np.array([np.abs(user_similarity).sum(axis=1)]).T


def calc_sleep_quality(sleep_id):
    quality = 0
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT s.email FROM sleeps s where s.sleep = \"{sleep_id}\";")
    email = mycursor.fetchall()[0][0]
    mycursor.execute(f"SELECT (SUM(CASE WHEN ss.type IN (2, 4, 5, 6) THEN TIMESTAMPDIFF(SECOND, ss.start, ss.end) ELSE 0 END) / SUM(TIMESTAMPDIFF(SECOND, ss.start, ss.end))) * 100 AS percentage1, (SUM(CASE WHEN ss.type IN (6) THEN TIMESTAMPDIFF(SECOND, ss.start, ss.end) ELSE 0 END) / SUM(TIMESTAMPDIFF(SECOND, ss.start, ss.end))) * 100 AS percentage2 FROM sleeps s JOIN sleep_stages ss ON s.sleep = ss.sleep WHERE s.sleep = \"{sleep_id}\";")
    percents = mycursor.fetchall()
    percent_sleep = int(percents[0][0])
    percent_rem = int(percents[0][1])
    mycursor.execute(f"SELECT SUM(TIMESTAMPDIFF(MINUTE, ss.start, ss.end)) AS total_sleep_duration FROM sleeps s JOIN sleep_stages ss ON s.sleep = ss.sleep WHERE s.email = \"{email}\" AND ss.end >= (DATE_SUB((select MAX(st.end) from sleep_stages st where st.sleep = \"{sleep_id}\"), INTERVAL 24 HOUR)) AND ss.start <= (select MAX(st.end) from sleep_stages st where st.sleep = \"{sleep_id}\");")
    hours_of_sleep = mycursor.fetchall()[0][0]
    mycursor.execute(f"SELECT s.sleep, s.email, cast((MIN(time_to_sec(ss.start)/60)) as unsigned), cast((MAX(time_to_sec(ss.end)/60)) as unsigned) FROM smart_sleeper.sleeps as s right join smart_sleeper.sleep_stages as ss on ss.sleep = s.sleep where s.email = \"{email}\" AND s.date >= DATE_SUB((select sle.date from sleeps sle where sle.sleep = \"{sleep_id}\"), INTERVAL 8 DAY) And s.date <= (select sle.date from sleeps sle where sle.sleep = \"{sleep_id}\") group by s.sleep;")
    records = mycursor.fetchall()

    count_start = 0
    count_end = 0
    sum_start = [0, 0]
    sum_end = [0, 0]
    for record in records:
        if int(record[0]) == sleep_id:
            start_hour = int(record[2])
            end_hour = int(record[3])
    for record in records:
        if int(record[0]) == sleep_id:
            continue
        dist = dist_between_hours(start_hour, int(record[2]))
        if dist < 30:
            count_start += 1
        elif dist < 60:
            sum_start[0] += 1
            sum_start[1] += dist
        dist = dist_between_hours(end_hour, int(record[3]))
        if dist < 30:
            count_end += 1
        elif dist < 60:
            sum_end[0] += 1
            sum_end[1] += dist
    if count_start >= 5:
        quality += 2
    else:
        quality += (count_start / 5) * 2
        if sum_start[0] > 0:
            quality += ((sum_start[1] - (30 * sum_start[0])) / (30 * sum_start[0])) * ((min(5 - count_start, sum_start[0]) / 5) * 2)
    if count_end >= 5:
        quality += 2
    else:
        quality += (count_end / 5) * 2
        if sum_end[0] > 0:
            quality += ((sum_end[1] - (30 * sum_end[0])) / (30 * sum_end[0])) * ((min(5 - count_end, sum_end[0]) / 5) * 2)

    if hours_of_sleep >= 420: # 7 hours of sleep at least in the last 24 hours
        quality += 2
    elif hours_of_sleep >= 300:
        quality += float((hours_of_sleep - 300) / 120) * 2

    if percent_sleep >= 85:
        quality += 2
    elif percent_sleep >= 60:
        quality += ((percent_sleep - 60) / 25) * 2

    if percent_rem >= 23:
        quality += 2
    elif percent_rem >= 15:
        quality += ((percent_rem - 15) / 8) * 2
    sql = "UPDATE sleeps SET quality = %s WHERE sleep = %s"
    val = (min(int(quality) + 1, 10), sleep_id)
    mycursor.execute(sql, val)
    mydb.commit()
    Util.close_db(mydb)


# the app asks if it should start waking up the user, the server returns how many minutes before starting the alarm
# 1 awake, 2 sleep, 3 out-of-bed, 4 light sleep, 5 deep sleep, 6 rem
def start_awakening(now, wake_time, alarm_start, time_from_rem):
    rem_time = dist_between_hours(now, time_from_rem)
    if rem_time >= 25:
        return alarm_start
    return min(alarm_start + rem_time, wake_time)


def get_alert_time(sleep_id, alarm_start):
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT type AS appearance_count FROM sleep_stages WHERE sleep = \"{sleep_id}\" AND end >= DATE_SUB(NOW(), INTERVAL 10 MINUTE) GROUP BY type ORDER BY appearance_count DESC LIMIT 1;")
    type = int(mycursor.fetchall()[0][0])
    Util.close_db(mydb)
    if type == 5 or type == 6:
        return alarm_start + 10
    return alarm_start



def update_alarm_start(rate, user):
    if rate == 3:
        return
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute(f"select start_music_sec from alarm_start a where a.email = \"{user}\";")
    alarm_start = int(mycursor.fetchall()[0][0])

    if rate == 1:
        update = -600
    if rate == 1.5:
        update = -300
    if rate == 2:
        update = -180
    if rate == 2.5:
        update = -60
    if rate == 3.5:
        update = 60
    if rate == 4:
        update = 180
    if rate == 4.5:
        update = 300
    if rate == 5:
        update = 600
    sql = "UPDATE alarm_start SET start_music_sec = %s WHERE email = %s"
    val = (max(alarm_start + update, 0), user)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()


# arr = get_users_from_db()
#rec = Recommender().train(get_users_from_db(), get_sleep_from_db())
rec = Recommender()
rec.train(get_users_from_db(), get_sleep_from_db())
# update_alarm_start(1, "artten12380@gmail.com")
# calc_sleep_quality(4)
#get_pred(arr)


def check_if_sleep_registered(milliseconds, email):
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()
    datetime.datetime.fromtimestamp(milliseconds / 1000.0)
    date = datetime.datetime.fromtimestamp(milliseconds / 1000.0)
    sql = "SELECT id FROM sleep_stages WHERE end = %s "
    values = date.strftime("%Y-%m-%d %H:%M:%S")
    mycursor.execute(sql, (values,))
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')
    for id in result:
        sql = "SELECT * FROM sleeps WHERE email = '" + email + "' and id = '" + id[0] + "'"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        if result:
            mydb.commit()
            mycursor.close()
            return 1
    mydb.commit()
    mycursor.close()
    return 0


def get_sleep_id_for_rating(email):
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()
    sql = "SELECT max(sleep) FROM sleeps WHERE email = %s"
    values = email
    mycursor.execute(sql, (values,))
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    mycursor.close()
    if result:
        return result[0][0]
    return 0


def get_wake_time(email):
    today = date.today()

    d1 = today.strftime("%d/%m/%Y")
    now = datetime.datetime.now()
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()

    sql = "select * from schedule where " \
          "email = '" + email + "'" \
          " and date = '" + d1 + "'" \
          "group by id"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    # return str(result[-1][0])
    if len(result) > 0:
        if not result[-1][3]:
            return "not"
        else:
            if (str(now.hour) > result[-1][4].split(":")[0])\
                    or (str(now.hour) == result[-1][4].split(":")[0] and str(now.minute) > result[-1][4].split(":")[1]):
                tomorrow = today + timedelta(1)
                d2 = tomorrow.strftime("%d/%m/%Y")
                mysql = Util.connect_to_db()
                mycursor = mysql.cursor()

                sql = "select * from schedule where " \
                      "email = '" + email + "'" \
                      " and date = '" + d2 + "'" \
                      "group by id"
                mycursor.execute(sql)
                result = mycursor.fetchall()
                mysql.commit()
                Util.close_db(mysql)
                if len(result) > 0:
                    if not result[0][3]:
                        return "not"
                    else:
                        return result[0][4]
            else:
                return result[-1][4]
    tomorrow = today + timedelta(1)
    day_of_the_week = get_day_of_the_week((today.weekday() + 1) % 7)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select * from schedule where " \
          "email = '" + email + "'" \
          " and day = '" + day_of_the_week + "'" \
          "group by id"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)

    if len(result) > 0:
        if not result[-1][3]:
            return "not"
        else:
            if (str(now.hour) > result[-1][4].split(":")[0])\
                    or (str(now.hour) == result[-1][4].split(":")[0] and str(now.minute) > result[-1][4].split(":")[1]):
                mysql = Util.connect_to_db()
                mycursor = mysql.cursor()
                day_of_the_week = get_day_of_the_week((tomorrow.weekday() + 1) % 7)
                sql = "select * from schedule where " \
                      "email = '" + email + "'" \
                      " and day = '" + day_of_the_week + "'" \
                      "group by id"
                mycursor.execute(sql)

                result = mycursor.fetchall()
                mysql.commit()
                Util.close_db(mysql)
                if not result[-1][3]:
                    return "not"
                else:
                    return result[-1][4]
            else:
                return result[-1][4]
    return "not"


def get_day_of_the_week(day):
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday"]
    return weekdays[day]


def get_all_futere_alarms(email):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select * from schedule where email = '" + email + "'"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    answer = ""
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday"]
    today = datetime.datetime.now()
    for r in result:
        if r[2] in weekdays:
            answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
        else:
            if int(today.year) < int(r[5].split("/")[2]):
                answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
            if int(today.year) == int(r[5].split("/")[2]):
                if int(today.month) < int(r[5].split("/")[1]):
                    answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                if int(today.month) == int(r[5].split("/")[1]):
                    if int(today.day) < int(r[5].split("/")[0]):
                        answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                    if int(today.day) == int(r[5].split("/")[0]):
                        if r[4] != '0':
                            if int(today.hour) < int(r[4].split(":")[0]):
                                answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                            if int(today.hour) == int(r[4].split(":")[0]):
                                if int(today.minute) < int(r[4].split(":")[1]):
                                    answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                                if int(today.minute) == int(r[4].split(":")[1]):
                                    if int(today.second) < int(r[4].split(":")[2]):
                                        answer = answer + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
    return answer


def get_all_qulity_of_sleep(email):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select sleep from sleeps where email = '" + email + "' order by date DESC "
    mycursor.execute(sql)
    sleep_id = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    ans = get_sleep_stats(email)
    for id in sleep_id:
        tmp = get_sleep_str_to_send(id[0])
        if tmp != None:
            ans = ans +tmp
    return ans


def get_sleep_stats(email):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = f"select avg(s.quality), avg(TIMESTAMPDIFF(MINUTE, (SELECT start FROM sleep_stages WHERE sleep = s.sleep ORDER BY start ASC LIMIT 1), (SELECT end FROM sleep_stages WHERE sleep = s.sleep ORDER BY end DESC LIMIT 1))) from sleeps as s where s.email = \"{email}\";"
    mycursor.execute(sql)
    stats = mycursor.fetchall()[0]
    ans = ""
    if stats[0] is not None:
        ans = ans + str(round(stats[0], 1)) + ","
    else:
        ans = ans + "None" + ","
    if stats[1] is not None:
        ans = ans + str(round(stats[1], 1)) + ","
    else:
        ans = ans + "None" + ","
    sql = f"select avg(s.quality), avg(TIMESTAMPDIFF(MINUTE, (SELECT start FROM sleep_stages WHERE sleep = s.sleep ORDER BY start ASC LIMIT 1), (SELECT end FROM sleep_stages WHERE sleep = s.sleep ORDER BY end DESC LIMIT 1))) from sleeps as s where s.email = \"{email}\" AND s.date >= CURDATE() - INTERVAL 7 DAY;"
    mycursor.execute(sql)
    stats = mycursor.fetchall()[0]
    if stats[0] is not None:
        ans = ans + str(round(stats[0], 1)) + ","
    else:
        ans = ans + "None" + ","
    if stats[1] is not None:
        ans = ans + str(round(stats[1], 1)) + "&"
    else:
        ans = ans + "None" + "&"
    mysql.commit()
    Util.close_db(mysql)
    return ans


def get_sleep_str_to_send(sleep_id):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select date from sleeps where sleep = " + str(sleep_id) + ""
    mycursor.execute(sql)
    date = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select min(start) from sleep_stages where sleep = " + str(sleep_id) + ""
    mycursor.execute(sql)
    start = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select max(end) from sleep_stages where sleep = " + str(sleep_id) + ""
    mycursor.execute(sql)
    end = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select quality from sleeps where sleep = " + str(sleep_id) + ""
    mycursor.execute(sql)
    quality = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    datetime.datetime.minute
    if start[0][0] != None and end[0][0] != None:
        return str(date[0][0].day) + "/" + str(date[0][0].month) + "/" + str(date[0][0].year) + ","\
            + start[0][0].strftime("%H:%M:%S") + "," \
            + end[0][0].strftime("%H:%M:%S") + ","\
            + str(quality[0][0]) + "&"


def get_settings(email):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select birthday,gender,height,weight from users where email = '" + email + "'"
    mycursor.execute(sql)
    ret = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    gender = "male"
    if ret[0][1] == 1:
        gender = "female"
    return str(ret[0][0].day) + "/" + str(ret[0][0].month) + "/" + str(ret[0][0].year)  \
        + "&" + gender + "&" + str(ret[0][2]) + "&" + str(ret[0][3])


def update_settings(email, birthday, gender, height, weight):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    birth = datetime.datetime.strptime(birthday, '%d/%m/%Y').date()
    ge = 1
    if gender == "female":
        ge = 0
    sql = "update users set birthday = '" + birth.strftime("%Y-%m-%d") + "'" \
          + ", gender = " + str(ge) + "" \
          + ", height = " + height + "" \
          + ", weight = " + weight + "" \
          + " where email = '" + email + "'"
    mycursor.execute(sql)
    ret = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)


def get_sleeping_time(email, wake_time):
    wake_time_int = int(wake_time.split(":")[0]) * 60 + int(wake_time.split(":")[1])
    ans = rec.predict_given_end_time(wake_time_int, email)
    hour = int(ans/60)
    minutes = int(ans % 60)
    return str(hour).zfill(2) + ":" + str(minutes).zfill(2) + ":00"


def update_alarm_start(rate, user):
    if rate == 3:
        return
    mydb = Util.connect_to_db()

    mycursor = mydb.cursor()

    mycursor.execute(f"select start_music_sec from alarm_start a where a.email = '" + user + "';")
    alarm_start = int(mycursor.fetchall()[0][0])

    if rate == 1:
        update = -600
    if rate == 1.5:
        update = -300
    if rate == 2:
        update = -180
    if rate == 2.5:
        update = -60
    if rate == 3.5:
        update = 60
    if rate == 4:
        update = 180
    if rate == 4.5:
        update = 300
    if rate == 5:
        update = 600
    sql = "UPDATE alarm_start SET start_music_sec = %s WHERE email = %s"
    val = (max(alarm_start + update, 0), user)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()


def get_when_to_wake_up(email, sleep_time):
    wake_time_int = int(sleep_time.split(":")[0]) * 60 + int(sleep_time.split(":")[1])
    ans = rec.predict_given_start_time(wake_time_int, email)
    print("anss")
    print(ans)
    print("anss1")
    hour = int(ans / 60)
    minutes = int(ans % 60)
    return str(hour).zfill(2) + ":" + str(minutes).zfill(2) + ":00"

def check_date_exist(email, date):
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select * from schedule where email = '"+email+"' and date = '"+date+"'"
    mycursor.execute(sql)
    ret = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    if len(ret) > 0:
        return True
    return False


def add_user(email, password, birthday, gender, height, weight):
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
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Sunday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Monday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Tuesday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Wednesday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Thursday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Friday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    sql = "insert into schedule (email, day, action, hour, date) " \
          "values (%s, %s, %s, %s, %s);"

    vals = (email, "Saturday", "0", "0", "0")
    result = mycursor.execute(sql, vals)
    mysql.commit()

    Util.close_db(mysql)
    if not result:
        return "somthing went wrong"
    return "ok"


def add_sleep(email, wake_date, quality):
    global sleep_id
    mydb = Util.connect_to_db()
    if not check_if_sleep_registered(int(wake_date), email):
        mycursor = mydb.cursor()
        mycursor.execute("select start_music_sec from alarm_start where email = '" + email + "';")
        result = mycursor.fetchall()
        min_before = result[0][0] / 60

        wake_date = datetime.datetime.fromtimestamp(float(wake_date) / 1000.0)
        wake_date = wake_date.strftime("%Y-%m-%d")

        sql = "INSERT INTO sleeps (email, date, quality, min_before)" \
              " VALUES (%s, %s, %s, %s)"
        vals = [(email, wake_date, quality, min_before)]
        mycursor.executemany(sql, vals)

        mydb.commit()

        mycursor.execute("select max(sleep) from sleeps where email = '" + email + "';")
        result = mycursor.fetchall()
        Util.close_db(mydb)
        sleep_id = result[0][0]
        return "ok"
    else:
        return "not ok"


def add_sleep_stages(start, end, sleep_type):
    global sleep_id
    if sleep_id != 0:
        try:
            sleep = sleep_id
            mydb = Util.connect_to_db()

            mycursor = mydb.cursor()
            if start == "done":
                sleep_id = 0
                return "need rating"

            start = datetime.datetime.fromtimestamp(float(start) / 1000.0)
            start = start.strftime("%Y-%m-%d %H:%M:%S")

            end = datetime.datetime.fromtimestamp(float(end) / 1000.0)
            end = end.strftime("%Y-%m-%d %H:%M:%S")

            sql = "INSERT INTO sleep_stages (sleep, start, end, type)" \
                  " VALUES (%s, %s, %s, %s)"
            vals = [(sleep, start, end, sleep_type)]
            mycursor.executemany(sql, vals)

            mydb.commit()
            mycursor.close()
            calc_sleep_quality(sleep_id)
            Util.close_db(mydb)
            return "ok"
        except Exception as e:
            print(e)
            return "not ok"
    return "not ok no try"


def add_alarm(date, day, action, email, hour):
    if date == "" and day == "Date":
        return "can't set"
    if date == "":
        date = 0
        hour = 0
    if day == "Date":
        day = 0
    if action == "false":
        action = 0
    if action == "true":
        action = 1
    if day != 0:
        mysql = Util.connect_to_db()
        mycursor = mysql.cursor()

        sql = "UPDATE schedule SET action = %s , hour = %s , date = '0'  WHERE email = %s and day = %s"
        vals = (action, hour, email, day)
        result = mycursor.execute(sql, vals)
        mysql.commit()
        Util.close_db(mysql)
        return "ok"
    try:
        if check_date_exist(email, date):
            mysql = Util.connect_to_db()
            mycursor = mysql.cursor()

            sql = "UPDATE schedule SET action = %s , hour = %s , day = '0'  WHERE email = %s and date = %s"
            vals = (action, hour, email, date)
            result = mycursor.execute(sql, vals)
            mysql.commit()
            Util.close_db(mysql)
            return "ok"
        else:
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


def add_rating(email, rate):
    sleep_id = get_sleep_id_for_rating(email)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select * from sleep_rating where sleep_id = " + str(sleep_id) + ""
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    if result:
        mysql = Util.connect_to_db()
        mycursor = mysql.cursor()
        update_alarm_start(float(rate), email)
        sql = "UPDATE sleep_rating SET rate = %s WHERE sleep_id = %s"
        vals = (rate, sleep_id)
        mycursor.execute(sql, vals)
        result = mycursor.fetchall()
        mysql.commit()
        Util.close_db(mysql)
        if result:
            return "somthing went wrong"
        return "ok"
    else:
        mysql = Util.connect_to_db()
        mycursor = mysql.cursor()
        update_alarm_start(float(rate), email)
        sql = "INSERT INTO sleep_rating (email, sleep_id, rate)" \
              " VALUES (%s, %s, %s)"
        vals = (email, sleep_id, rate)
        mycursor.execute(sql, vals)
        result = mycursor.fetchall()
        mysql.commit()
        Util.close_db(mysql)

        if result:
            return "somthing went wrong"
        return "ok"


def get_last_sleep(email):
    sleep_id = get_sleep_id_for_rating(email)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select min(start) from sleep_stages where sleep = " + str(sleep_id) + ""
    mycursor.execute(sql)
    start = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    mysql = Util.connect_to_db()
    mycursor = mysql.cursor()
    sql = "select max(end) from sleep_stages where sleep = " + str(sleep_id) + ""
    mycursor.execute(sql)
    end = mycursor.fetchall()
    mysql.commit()
    Util.close_db(mysql)
    if not start or not end:
        return "somthing went wrong"
    return start[0][0].strftime("%m/%d/%Y %H:%M:%S") + "," + end[0][0].strftime("%m/%d/%Y %H:%M:%S") + "&"


rec = Recommender()
rec.train(get_users_from_db(), get_sleep_from_db())


