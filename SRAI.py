import time

import mysql
import pandas as pd
import numpy as np
import math
from fastdtw import dtw
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.cluster import KMeans
from collections import Counter


def get_sleep_of_user_from_db(email):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="223333",
        database="smart_sleeper"
    )

    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT s.sleep, s.email, cast(COALESCE(sr.rate, 3) as float), cast((MIN(time_to_sec(ss.start)/60)) as unsigned), cast((MAX(time_to_sec(ss.end)/60)) as unsigned) FROM smart_sleeper.sleeps as s right join smart_sleeper.sleep_stages as ss on ss.sleep = s.sleep LEFT JOIN smart_sleeper.sleep_rating AS sr ON sr.sleep_id = s.sleep where s.email = \"{email}\" group by s.sleep;")
    result = mycursor.fetchall()
    # predict(ratings.to_numpy(), user_similarity, type='user')

    mydb.commit()
    arr = np.array(result)

    mycursor.close()

    return arr


# return true or false if h1 is less than "time" minutes from h2
def two_hours_close(h1, h2, time):
    h1 = int(h1)
    h2 = int(h2)
    if (max(h1, h2) - min(h1, h2)) < time:
        return True
    if (min(h1, h2) + 1440) - max(h1, h2) < time:
        return True
    return False


def dist_between_hours(h1, h2):
    h1 = int(h1)
    h2 = int(h2)
    dist = max(h1, h2) - min(h1, h2)
    dist2 = (min(h1, h2) + 1440) - max(h1, h2)
    return min(dist2, dist)


def mass_center(data):
    kmeans = KMeans(init="random", n_clusters=10, tol=1)
    kmeans.fit(data.reshape(-1, 1))
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    unique, counts = np.unique(labels, return_counts=True)
    result = {}
    for i in range(len(unique)):
        result[centers[unique[i]]] = counts[i]
    return result


# given sleep start time of user recommend time for waking up receive the user sleep records, for the sake of
# convenience the format for a record is: start time, end time , rating
def recommend_wake_time(start_time, records):
    #mask = two_hours_close(records[:, 3], start_time, 120)
    #print(mask)
    relevant = []

    for i in range(len(records)):
        print(records[i][4])
        if two_hours_close(records[i][3], start_time, 120):
            relevant.append(records[i])

    #relevant = (records[mask])[0]
    relevant = np.array(relevant)
    print(relevant)
    if len(relevant) == 0:
        return start_time + 480
    return ((np.array(relevant[:, 4]).astype(float) * np.array(relevant[:, 2]).astype(float)).sum()) / (np.array(relevant[:, 2]).astype(float).sum())


# given sleep end time of user recommend time for starting to sleep, receive the user sleep records, for the sake of
# convenience the format for a record is: start time, end time , rating
def recommend_sleep_time(wake_time, records):
    #mask = two_hours_close(records[:, 3], start_time, 120)
    #print(mask)
    relevant = []
    for i in range(len(records)):
        if two_hours_close(records[i][4], wake_time, 120):
            relevant.append(records[i])

    #relevant = (records[mask])[0]
    relevant = np.array(relevant)
    if len(relevant) == 0:
        time = wake_time - 480
        if time < 0:
            time += 1440
        return time
    return ((np.array(relevant[:, 3]).astype(float) * np.array(relevant[:, 2]).astype(float)).sum()) / (np.array(relevant[:, 2]).astype(float).sum())


# this similarity is not symmetric
def hours_array_sim(hours1, hours2):
    div = len(hours1)
    sim_score = 0
    for k1, val1 in hours1.items():
        sum_val = 0
        for k2, val2 in hours2.items():
            if two_hours_close(k1, k2, 60):
                sum_val += (1 - (dist_between_hours(k1, k2) / 60)) * (min((val2 / val1), 1))
        sim_score += min(1.0, sum_val / div)
    return min(sim_score, 1.0)


class Recommender:
    def __init__(self, strategy='user'):
        self.strategy = strategy
        self.content_sim = np.NaN
        self.similarity = np.NaN
        self.matrix = np.NaN
        self.recNum = 2
        self.users_list = np.NaN

    def organize_user(self, users):
        self.users_list = users[:, 0]
        return users[:, 1:5]

    def organize_sleep_start(self, sleeps):
        arr = []

        for email in self.users_list:
            #arr[i] = sleeps[sleeps[:, 1] == email][:, 3]
            hours = np.array(sleeps[sleeps[:, 1] == email][:, 3]).astype(int)
            counter = Counter(hours)
            arr.append(counter)
            #if len(hours) < 10:
            #    arr.append({val: 1 for val in hours})
            #else:
            #    arr.append(mass_center(hours))

        arr = np.array(arr, dtype=object)
        return arr

    def organize_sleep_end(self, sleeps):
        arr = []

        for email in self.users_list:
            #arr[i] = sleeps[sleeps[:, 1] == email][:, 3]
            hours = np.array(sleeps[sleeps[:, 1] == email][:, 4]).astype(int)
            counter = Counter(hours)
            arr.append(counter)
            #if len(hours) < 10:
            #    arr.append({val: 1 for val in hours})
            #else:
            #    arr.append(mass_center(hours))

        arr = np.array(arr, dtype=object)
        return arr

    # receive data of 2 users and calc similarity
    def content_sim_between_2users(self, a, b):
        weights = np.array([0.25, 0.25, 0.25, 0.25])
        diff_arr = np.array([])
        years = 1825
        similarity = 0
        # age is similar if at the very least they are 5 years apart
        if abs(a[0] - b[0]) < years:
            similarity += (1 - (abs((a[0] - b[0]) / 1825))) * weights[0]
            print(similarity)
        # is same gender
        if a[1] == b[1]:
            similarity += weights[1]
        # height is similar if at the very least they are 20 cem apart
        if abs(a[2] - b[2]) < 0.2:
            similarity += (1 - (abs((a[2] - b[2]) / 0.2))) * weights[2]
        # weight is similar if at the very least they are 15 kilos apart
        if abs(a[3] - b[3]) < 15:
            similarity += (1 - (abs((a[3] - b[3]) / 15))) * weights[3]
        return similarity

    # this function receive a matrix containing all the users data, and a function that receive info of 2 people and
    # return similarity between them
    def calc_similarity(self, matrix, sim_func):
        self.matrix = matrix
        # a = matrix.shape
        a = len(self.users_list)
        result = np.zeros((a, a))
        for i in range(a):
            result[i][i] = 1
        for i in range(a):
            for j in range(a):
                result[i][j] = sim_func(matrix[i], matrix[j])
        #for i in range(a):
         #   for j in range(i + 1, a):
          #      result[i][j] = sim_func(matrix[i], matrix[j])
           #     result[j][i] = result[i][j]
        return result

    # this function receive a matrix of records of different id's and sim func return similarity
    # def get_similarity_given_multi_records_per_person(self, matrix, sim_func):

    # this function receive all the needed database data on all users and create a similarity matrix
    def train(self, users, sleep_records):
        # each factor is given different weight in the similarity matrix
        weights = np.array([1, 3])
        # first organize the data into structure that can be sent to
        content_mat = self.organize_user(users)
        # sleep has many factors that can be considered, start time, end time, and how long the sleep was,
        # each can be considered. for now sleep1 is start time
        sleep_mat_start = self.organize_sleep_start(sleep_records)
        sleep_mat_end = self.organize_sleep_end(sleep_records)

        self.content_sim = self.calc_similarity(content_mat, self.content_sim_between_2users)
        start_sim_mat = self.calc_similarity(sleep_mat_start, hours_array_sim)
        end_sim_mat = self.calc_similarity(sleep_mat_end, hours_array_sim)
        # self.sleep_start_sim = self.calc_similarity(sleep_mat1, dtw)
        print(self.content_sim)
        print(start_sim_mat)
        print(end_sim_mat)

        self.similarity = self.content_sim * 0.4 + start_sim_mat * 0.3 + end_sim_mat * 0.3
        print("similarity:")
        print(self.similarity)
        print("user_list:")
        print(self.users_list)

    def predict_given_start_time(self, start_time, user):
        recommended_end_time = np.array([])
        index = (np.where(self.users_list == user)[0])[0]
        # get records of the self.recNum users with highest similarity to user
        highest_sim_index = np.flip(np.argsort(self.similarity[index]))[:self.recNum]
        # highest_sim = self.similarity[index][highest_sim_index]
        sum_hour = 0
        for ind in highest_sim_index:
            sum_hour += recommend_wake_time(start_time, get_sleep_of_user_from_db((self.users_list[highest_sim_index])[0]))
        return sum_hour / self.recNum

    def predict_given_end_time(self, end_time, user):
        recommended_end_time = np.array([])
        index = (np.where(self.users_list == user)[0])[0]
        # get records of the self.recNum users with highest similarity to user
        highest_sim_index = np.flip(np.argsort(self.similarity[index]))[:self.recNum]
        # highest_sim = self.similarity[index][highest_sim_index]
        sum_hour = 0
        for ind in highest_sim_index:
            # sum_hour += recommend_sleep_time(end_time, get_sleep_of_user_from_db((self.users_list[highest_sim_index])[0]))
            sum_hour += recommend_sleep_time(end_time, get_sleep_of_user_from_db(self.users_list[ind]))
        return sum_hour / self.recNum
