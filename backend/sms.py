import requests
import json

url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

payload = json.dumps({
  "code": "w36asdmxr5alzk8",
  "sender": "+983000505",
  "recipient": "09352554850",
  "variable": {
    "verification-code": "12345"
  }
})

headers = {
  'apikey': 'OWYxMTZkZDUtOTY5Ni00NWZiLTllNGYtMjJjYzZlYTQ0ODk2NTczNDU5MDUwZWU1YjkyYjRkY2QyM2VhNTUwZWU4ZjI',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
