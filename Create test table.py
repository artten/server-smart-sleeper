import Util
import mysql.connector


mydb = mysql.connector.connect(
  host="localhost",
  user="artiom",
  password="password",
  database="smart_sleeper"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE test (name VARCHAR(255), age INT)")

sql = "INSERT INTO test (name, age) VALUES (%s, %s)"
val = [("John", 15), ("Cena", 54), ("Saar", 26)]
mycursor.executemany(sql, val)
mydb.commit()

mycursor.close()
