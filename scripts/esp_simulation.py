import requests
import random
import time

URL = "http://127.0.0.1:5000/sensor"

while True:

    data = {
        "ax": random.uniform(-2,2),
        "ay": random.uniform(-2,2),
        "az": random.uniform(-2,2),
        "gx": random.uniform(-250,250),
        "gy": random.uniform(-250,250),
        "gz": random.uniform(-250,250)
    }

    response = requests.post(URL,json=data)

    print("Sent:",data)
    print("Server:",response.text)

    time.sleep(1)