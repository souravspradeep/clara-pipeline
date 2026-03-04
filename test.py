import requests

r = requests.post(
    'https://concessive-gigi-unsettled.ngrok-free.dev/llm',
    json={'transcript': [{'role': 'user', 'content': 'Hello I need help'}]}
)
print("Status code:", r.status_code)
print("Response text:", r.text)