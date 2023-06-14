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

# mycursor.execute("CREATE TABLE schedule (id INT AUTO_INCREMENT PRIMARY KEY,"
#                  "email VARCHAR(255) ,"
#                  "day VARCHAR(255),"
#                  "action BOOLEAN,"
#                  "hour VARCHAR(255),"
#                  "date VARCHAR(255),"
#                  "FOREIGN KEY(email) REFERENCES users(email) )")
sql = "INSERT INTO schedule (email, day, action, hour, date)" \
      " VALUES (%s, %s, %s, %s, %s)"
vals = [("artten12380@gmail.com", "Sunday", True, "06:00:00", "0"),
        ("artten12380@gmail.com", "Monday", True, "09:00:00", "0"),
        ("artten12380@gmail.com", "Tuesday", True, "06:00:00", "0"),
        ("artten12380@gmail.com", "Wednesday", True, "08:00:00", "0"),
        ("artten12380@gmail.com", "Thursday", True, "06:00:00", "0"),
        ("artten12380@gmail.com", "Friday", False, "06:00:00", "0"),
        ("artten12380@gmail.com", "Thursday", False, "06:00:00", "0"),
        ("artten12380@gmail.com", "0", False, "0", "19/9/2023"),
        ("artten12380@gmail.com", "0", True, "10:00:00", "20/9/2023")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()

