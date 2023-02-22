import mysql.connector


def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="artiom",
        password="password",
        database="smart_sleeper"
    )


def close_db(db):
    db.close()

