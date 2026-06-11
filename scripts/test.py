import requests

url = "http://127.0.0.1:5000/send-alert"
data = {
    "location": "Home Living Room"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.text)
