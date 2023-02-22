import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="artiom",
  password="password"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE smart-sleeper")
