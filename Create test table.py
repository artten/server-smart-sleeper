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
val = ("John", 15)
mycursor.execute(sql, val)

mydb.commit()

sql = "INSERT INTO customers (name, age) VALUES (%s, %s)"
val = ("Cena", 54)
mycursor.execute(sql, val)

mydb.commit()

sql = "INSERT INTO customers (name, age) VALUES (%s, %s)"
val = ("Saar", 26)
mycursor.execute(sql, val)

mydb.commit()

mycursor.close()
