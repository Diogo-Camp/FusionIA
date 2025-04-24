import requests

res = requests.post(
    'http://localhost:11434/api/generate',
    json={"model": "llama3", "prompt": "Olá, quem é você?"}
)

print(res.json()['response'])
