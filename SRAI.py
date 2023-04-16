import time

import mysql
import pandas as pd
import numpy as np
import math
from fastdtw import dtw
from sklearn.metrics.pairwise import pairwise_distances


def get_sleep_of_user_from_db(email):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="223333",
        database="smart_sleeper"
    )

    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT s.sleep, s.email, cast(s.quality as unsigned), cast((MIN(time_to_sec(ss.start)/60)) as unsigned), cast((MAX(time_to_sec(ss.end)/60)) as unsigned) FROM smart_sleeper.sleeps as s right join smart_sleeper.sleep_stages as ss on ss.sleep = s.sleep where s.email = \"{email}\" group by s.sleep;")
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


# given sleep start time of user recommend time for waking up receive the user sleep records, for the sake of
# convenience the format for a record is: start time, end time , rating
def recommend_wake_time(start_time, records):
    #mask = two_hours_close(records[:, 3], start_time, 120)
    #print(mask)
    relevant = []
    for i in range(len(records)):
        if two_hours_close(records[i][3], start_time, 120):
            relevant.append(records[i])

    #relevant = (records[mask])[0]
    relevant = np.array(relevant)
    print(relevant)
    if len(relevant) == 0:
        return start_time + 480

    return ((np.array(relevant[:, 4]).astype(int) * np.array(relevant[:, 2]).astype(int)).sum()) / (np.array(relevant[:, 2]).astype(int).sum())


# def dist_from_hours()


class Recommender:
    def __init__(self, strategy='user'):
        self.strategy = strategy
        self.content_sim = np.NaN
        self.similarity = np.NaN
        self.matrix = np.NaN
        self.recNum = 1
        self.users_list = np.NaN

    def organize_user(self, users):
        self.users_list = users[:, 0]
        return users[:, 1:5]

    def organize_sleep_start(self, sleeps):
        arr = (np.array([sleeps[sleeps[:, 1] == email][:, 3] for email in self.users_list])).astype(int)
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
        if a[1] == b[1]:
            similarity += weights[1]
        # height is similar if at the very least they are 20 cem apart
        if abs(a[2] - b[2]) < 0.2:
            similarity += (1 - (abs((a[2] - b[2]) / 0.2))) * weights[2]
        # height is similar if at the very least they are 20 cem apart
        if abs(a[2] - b[2]) < 20:
            similarity += (1 - (abs((a[3] - b[3]) / 20))) * weights[3]
        return similarity

    # this function receive a matrix containing all the users data, and a function that receive info of 2 people and
    # return similarity between them
    def calc_similarity(self, matrix, sim_func):
        self.matrix = matrix
        a, b = matrix.shape
        result = np.zeros((a, a))
        for i in range(a):
            for j in range(i + 1, a):
                result[i][j] = sim_func(matrix[i], matrix[j])
                result[j][i] = result[i][j]
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
        #sleep_mat1 = self.organize_sleep_start(sleep_records)

        self.content_sim = self.calc_similarity(content_mat, self.content_sim_between_2users)
        # self.sleep1_sim = self.calc_similarity(sleep_mat1, dtw)

        # self.similarity = (self.content_sim * weights[0] + self.sleep1_sim * weights[1]) / np.sum(weights)
        self.similarity = self.content_sim
        print("similarity:")
        print(self.similarity)
        print("user_list:")
        print(self.users_list)

    def predict_given_start_time(self, start_time, user):
        # get records of user from database, for continuity
        pass
        recommended_end_time = np.array([])
        index = (np.where(self.users_list == user)[0])[0]
        # get records of the self.recNum users with highest similarity to user
        highest_sim_index = np.flip(np.argsort(self.similarity[index]))[:self.recNum]
        # highest_sim = self.similarity[index][highest_sim_index]
        sum_hour = 0
        for ind in highest_sim_index:
            sum_hour += recommend_wake_time(start_time, get_sleep_of_user_from_db((self.users_list[highest_sim_index])[0]))
        return sum_hour / self.recNum
