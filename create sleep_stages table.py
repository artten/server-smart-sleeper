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

mycursor.execute("CREATE TABLE sleep_stages (id INT AUTO_INCREMENT PRIMARY KEY,"
                 "sleep INT ,"
                 "start DATETIME,"
                 "end DATETIME,"
                 "type INT,"
                 "FOREIGN KEY(sleep) REFERENCES sleeps(sleep) )")
sql = "INSERT INTO sleep_stages (sleep, start, end, type)" \
      " VALUES (%s, %s, %s, %s)"
vals = [("1", "2023-3-13 23:50:00", "2023-3-13 23:51:00", "1"),
        ("1", "2023-3-13 23:51:00", "2023-3-13 23:52:00", "2"),
        ("1", "2023-3-13 23:52:00", "2023-3-13 23:53:00", "3")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()
