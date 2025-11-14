from pprint import pprint

import requests

PATH = "/api/events"
BASE_URL = "http://localhost:8002"  # 127.0.0.1
ENDPOINT = f"{BASE_URL}{PATH}"

response = requests.get(ENDPOINT, timeout=2.5)
print("ok", response.ok)
if response.ok:
    data = response.json()
    pprint(data)
