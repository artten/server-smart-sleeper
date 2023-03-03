import mysql.connector


def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="artiom",
        password="password",
        database="smart_sleeper"
    )


def execute_sql(db, sql):
    mycursor = db.cursor()
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    db.commit()
    return myresult

def close_db(db):
    db.close()

