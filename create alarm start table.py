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

mycursor.execute("CREATE TABLE alarm_start (id INT AUTO_INCREMENT PRIMARY KEY,"
                 "email VARCHAR(255) ,"
                 "start_music_sec INT,"
                 "FOREIGN KEY(email) REFERENCES users(email) )")
sql = "INSERT INTO alarm_start (email, start_music_sec)" \
      " VALUES (%s, %s)"
vals = [("artten12380@gmail.com", "12000"),
        ("yosi123@gmail.com", "12000"),
        ("marina99@gmail.com", "6000")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()

