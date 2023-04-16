from datetime import timedelta
import mysql.connector
import pandas as pd
import numpy as np
import datetime
from sklearn.metrics.pairwise import pairwise_distances


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
    print(date.strftime("%d-%m-%Y %H:%M:%S"))
    mycursor.execute("select * from sleep_stages where start = " + date.strftime("%d-%m-%Y %H:%M:%S") + ";")
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    mycursor.close()

check_if_sleep_registered(1681616940000)

