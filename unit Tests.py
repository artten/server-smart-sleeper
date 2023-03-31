import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="artiom",
  password="password",
  database="smart_sleeper"
)
mycursor = mydb.cursor(buffered=True)


def test_is_all_tables_exist(tables_names):
    mycursor.execute("SHOW TABLES;")
    result = mycursor.fetchall()
    mydb.commit()
    counter = 0
    for table in result:
        if table[0] in tables_names:
            counter += 1
        if not table[0] in tables_names:
            return False
    if counter != len(tables_names):
        return False
    return True


def add_new_user():
    sql = "INSERT INTO users (email, password, birthday, gender, height, weight)" \
          " VALUES (%s, %s, %s, %s, %s, %s)"
    vals = [("test", "test", "1996-12-13", "1", "1.69", "68")]
    mycursor.executemany(sql, vals)
    mydb.commit()
    mycursor.execute("select email from users where email='test';")
    result = mycursor.fetchall()
    mydb.commit()
    if result:
        return True
    return False


def delete_test_user():
    mycursor.execute("select email from users where email='test';")
    result = mycursor.fetchall()
    mydb.commit()
    if result:
        mycursor.execute("delete from users where email='test';")
        mydb.commit()
        if mycursor.rowcount == 1:
            return True
    return False


def test_all():
    if not test_is_all_tables_exist(
            ["alarms", "customers", "sleep_rating", "sleep_stages", "sleeps", "test", "users"]):
        print("failed 1")
        return False
    if not add_new_user():
        print("failed 2")
        return False
    if not delete_test_user():
        print("failed 3")
        return False
    mycursor.close()


if __name__ == "__main__":
    test_all()
