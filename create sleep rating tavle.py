import Util
import mysql.connector
import datetime


mydb = mysql.connector.connect(
  host="localhost",
  user="artiom",
  password="password",
  database="smart_sleeper"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE sleep_rating (id INT AUTO_INCREMENT PRIMARY KEY,"
                 "email VARCHAR(255) ,"
                 "sleep_id INT,"
                 "rate FLOAT,"
                 "FOREIGN KEY(sleep_id) REFERENCES sleeps(sleep),"
                 "FOREIGN KEY(email) REFERENCES users(email) )")
sql = "INSERT INTO sleep_rating (email, sleep_id, rate)" \
      " VALUES (%s, %s, %s)"
vals = [("artten12380@gmail.com", "1", "3"),
        ("yosi123@gmail.com", "2", "3.5"),
        ("marina99@gmail.com", "3", "1")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()


mycursor.close()
