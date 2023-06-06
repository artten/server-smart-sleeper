from datetime import timedelta
import mysql.connector
import pandas as pd
import numpy as np
import datetime
from sklearn.metrics.pairwise import pairwise_distances
from SRAI import *


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
        user="root",
        password="223333",
        database="smart_sleeper"
    )

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
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="223333",
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


def get_sleep_from_db():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="223333",
        database="smart_sleeper"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT s.sleep, s.email, COALESCE(sr.rate, 3), cast((MIN(time_to_sec(ss.start)/60)) as unsigned), cast((MAX(time_to_sec(ss.end)/60)) as unsigned) FROM smart_sleeper.sleeps as s right join smart_sleeper.sleep_stages as ss on ss.sleep = s.sleep LEFT JOIN smart_sleeper.sleep_rating AS sr ON sr.sleep_id = s.sleep group by s.sleep;")
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    arr = np.array(result)
    count = 0
    for i in arr:
        arr[count][2] = float(i[2])
        arr[count][3] = int(i[3])
        arr[count][4] = int(i[4])
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


def calc_sleep_quality(sleep_id):
    quality = 0
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="223333",
        database="smart_sleeper"
    )

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
    print(records)

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
        quality += ((hours_of_sleep - 300) / 120) * 2

    if percent_sleep >= 85:
        quality += 2
    elif percent_sleep >= 60:
        quality += ((percent_sleep - 60) / 25) * 2

    if percent_rem >= 23:
        quality += 2
    elif percent_rem >= 15:
        quality += ((percent_rem - 15) / 8) * 2
    return quality


arr = get_users_from_db()
print(get_users_from_db())
print(get_sleep_from_db())
#rec = Recommender().train(get_users_from_db(), get_sleep_from_db())
rec = Recommender()
rec.train(get_users_from_db(), get_sleep_from_db())
print("given time 1400 predicted time:")
print(rec.predict_given_start_time(1400, "artten12380@gmail.com"))
calc_sleep_quality(4)
#get_pred(arr)
