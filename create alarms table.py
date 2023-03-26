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

mycursor.execute("CREATE TABLE users ( VARCHAR(255)  PRIMARY KEY,"
                 "password VARCHAR(255),"
                 "birthday DATE,"
                 "gender BOOLEAN,"
                 "height FLOAT,"
                 "weight FLOAT )")
sql = "INSERT INTO users (email, password, birthday, gender, height, weight)" \
      " VALUES (%s, %s, %s, %s, %s, %s)"
vals = [("artten12380@gmail.com", "123123123", "1996-12-13", "1", "1.69", "68"),
        ("yosi123@gmail.com", "123123123", "2002-11-11", "1", "2.0", "78"),
        ("marina99@gmail.com", "123123123", "1999-3-7", "0", "1.50", "54")]
mycursor.executemany(sql, vals)
mydb.commit()

mycursor.close()
