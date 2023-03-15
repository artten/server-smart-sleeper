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
                 "note TEXT,"
                 "FOREIGN KEY(email) REFERENCES users(email) )")
sql = "INSERT INTO sleeps (email, date, quality, note)" \
      " VALUES (%s, %s, %s, %s)"
vals = [("artten12380@gmail.com", "2023-3-13", "1", "lol lol"),
        ("yosi123@gmail.com", "2023-3-13", "3", "blue blue"),
        ("marina99@gmail.com", "2023-3-13", "5", "bla bla")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()
