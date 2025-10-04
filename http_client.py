import requests

url = ""

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Request failed:", response.status_code)