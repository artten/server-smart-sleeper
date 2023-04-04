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

mycursor.execute("CREATE TABLE sleeps (sleep INT AUTO_INCREMENT PRIMARY KEY,"
                 "email VARCHAR(255) ,"
                 "date DATE,"
                 "quality INT,"
                 "min_before FLOAT,"
                 "FOREIGN KEY(email) REFERENCES users(email) )")
sql = "INSERT INTO sleeps (email, date, quality, min_before)" \
      " VALUES (%s, %s, %s, %s)"
vals = [("artten12380@gmail.com", "2023-3-13", "1", "10"),
        ("yosi123@gmail.com", "2023-3-13", "3", "13"),
        ("marina99@gmail.com", "2023-3-13", "5", "11.1")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()
