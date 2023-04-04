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

mycursor.execute("CREATE TABLE alarms (id INT AUTO_INCREMENT PRIMARY KEY,"
                 "email VARCHAR(255) ,"
                 "wake_date DATE,"
                 "wake_time TIME,"
                 "sleep_date DATE,"
                 "sleep_time time,"
                 "FOREIGN KEY(email) REFERENCES users(email) )")
sql = "INSERT INTO alarms (email, wake_date, wake_time, sleep_date, sleep_time)" \
      " VALUES (%s, %s, %s, %s, %s)"
vals = [("artten12380@gmail.com", "2023-3-13", "22:00:00", "2023-3-14", "06:00:00"),
        ("yosi123@gmail.com", "2023-3-15", "22:00:00", "2023-3-16", "06:00:00"),
        ("marina99@gmail.com", "2023-3-16", "22:00:00", "2023-3-17", "06:00:00")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()


mycursor.close()
