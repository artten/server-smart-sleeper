from datetime import timedelta
import mysql.connector
import Util
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
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
    mydb = mysql.connector.connect(
        host="localhost",
        user="artiom",
        password="password",
        database="smart_sleeper"
    )

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


def get_reviews_from_db():
    mydb = mysql.connector.connect(
        host="localhost",
        user="artiom",
        password="password",
        database="smart_sleeper"
    )

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


def get_pred(arr):
    mean_user_rating = np.mean(arr, axis=1).reshape(-1, 1)
    print(mean_user_rating)
    ratings_diff = (arr - mean_user_rating)
    print(ratings_diff)
    user_similarity = 1 - pairwise_distances(ratings_diff, metric='cosine')
    print(user_similarity.shape)
    pred = mean_user_rating + user_similarity.dot(ratings_diff) / np.array([np.abs(user_similarity).sum(axis=1)]).T
    print(pred)


def check_if_sleep_registered(milliseconds):
    mydb = mysql.connector.connect(
    host="localhost",
    user="artiom",
    password="password",
    database="smart_sleeper"
    )

    mycursor = mydb.cursor()
    date = datetime.datetime.fromtimestamp(milliseconds / 1000.0)
    sql = "SELECT * FROM sleep_stages WHERE end = %s"
    values = date.strftime("%Y-%m-%d %H:%M:%S")
    mycursor.execute(sql, (values,))
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    print("result = ")
    print(result)
    print(date.strftime("%Y-%m-%d %H:%M:%S"))
    mycursor.close()
    if result:
        return 1
    return 0


def get_sleep_id_for_rating(email):
    mydb = mysql.connector.connect(
    host="localhost",
    user="artiom",
    password="password",
    database="smart_sleeper"
    )

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
    print(result)
    if len(result) > 0:
        if not result[0][3]:
            return "not"
        else:
            if str(now.hour) > result[0][4]:
                tomorrow = today + timedelta(1)
                print(tomorrow.weekday())
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
                return result[0][4]
    tomorrow = today + timedelta(1)
    day_of_the_week = get_day_of_the_week((tomorrow.weekday() + 1) % 7)
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
        if not result[0][3]:
            return "not"
        else:
            mysql = Util.connect_to_db()
            mycursor = mysql.cursor()
            day_of_the_week = get_day_of_the_week((tomorrow.weekday() + 2) % 7)
            sql = "select * from schedule where " \
                  "email = '" + email + "'" \
                  " and day = '" + day_of_the_week + "'" \
                  "group by id"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            mysql.commit()
            Util.close_db(mysql)
            if not result[0][3]:
                return "not"
            else:
                return result[0][4]
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
            answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
        else:
            if int(today.year) < int(r[5].split("/")[2]):
                answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
            if int(today.year) == int(r[5].split("/")[2]):
                if int(today.month) < int(r[5].split("/")[1]):
                    answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                if int(today.month) == int(r[5].split("/")[1]):
                    if int(today.day) < int(r[5].split("/")[0]):
                        answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                    if int(today.day) == int(r[5].split("/")[0]):
                        if r[4] != '0':
                            if int(today.hour) < int(r[4].split(":")[0]):
                                answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                            if int(today.hour) == int(r[4].split(":")[0]):
                                if int(today.minute) < int(r[4].split(":")[1]):
                                    answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
                                if int(today.minute) == int(r[4].split(":")[1]):
                                    if int(today.second) < int(r[4].split(":")[2]):
                                        answer = answer  + r[2] + "," + str(r[3]) + "," + r[4] + "," + r[5] + '&'
    return answer






