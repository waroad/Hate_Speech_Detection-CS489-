import requests

url = "http://127.0.0.1:5000/inference"
data = {"sentence": "이래서 여자는 게임을 하면 안된다"}

response = requests.post(url, json=data)
print("Response:", response.json())
