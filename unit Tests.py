import mysql.connector
import  backend

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
    backend.add_user('test', '112233', '1996-12-13', '1', '168', '87')
    mycursor.execute("select email from users where email='test';")
    result = mycursor.fetchall()
    mydb.commit()
    if result:
        return True
    return False


def add_sleep():
    backend.add_sleep("test", "1677812400000", "1")
    backend.add_sleep_stages("1677812400000", "1677816000000", "2")
    backend.add_sleep_stages("1677816000000", "1677819600000", "3")
    backend.add_sleep_stages("1677819600000", "1677823200000", "4")
    mycursor.execute("select * from sleep_stages where start = '2023-03-03 07:00:00'")
    result = mycursor.fetchall()
    if result:
        return 1
    return 0


def add_schedule():
    if backend.add_alarm("0", "Sunday", "1", "test", "09:00:00") == "ok":
        if backend.add_alarm("", "Date", "1", "test", "09:00:00") == "can't set":
            return 1
    return 0

def add_rating():
    if backend.add_rating("test", "3") == "ok":
        return 1

def test_all():
    if not test_is_all_tables_exist(
            ["alarms", "customers", "sleep_rating", "sleep_stages", "sleeps", "test", "users", "alarm_start", "schedule"]):
        print("failed 1")
        return False
    if not add_new_user():
        print("failed 2")
        return False
    if not add_sleep():
        print("failed 3")
        return False
    if not add_schedule():
        print("failed 4")
        return False
    if not add_rating():
        print("failed 5")
        return False
    print("All test passed")
    return True

    mycursor.close()


if __name__ == "__main__":
    test_all()
