import mysql.connector

num_min_in_day = 1440
min_in_8_hours = 480
min_in_2_hours = 120
min_in_1_hour = 60
days_in_5_years = 1825
height_sim = 0.2
weight_sim = 15
content_sim_weight = 0.25
content_met_weight = 0.4
hours_met_weight = 0.3
per_hour_sim_factor = 1.2


def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="223333",
        database="smart_sleeper"
    )


def execute_sql(db, sql):
    print(sql)
    mycursor = db.cursor()
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    db.commit()
    return myresult


def close_db(db):
    db.close()

