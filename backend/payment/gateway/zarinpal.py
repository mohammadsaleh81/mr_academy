import requests
import json
from django.conf import settings


def send_payment_request(amount, description, mobile=None, email=None):

    payload = {
        "merchant_id":"7580cc08-b6f3-43a3-af45-5eea2c53aa44",
        "amount": amount,  # Amount in Tomans (or Rials, specify with 'currency')
        "callback_url": settings.CALLBACK_URL,
        "description": description,
        "metadata": {}
    }

    if mobile:
        payload["metadata"]["mobile"] = mobile
    if email:
        payload["metadata"]["email"] = email

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.post(settings.ZP_API_REQUEST, data=json.dumps(payload), headers=headers, timeout=10)
    response.raise_for_status()
    result = response.json()
    return result



def send_verify(amount, authority):
    url = settings.ZP_API_VERIFY
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "merchant_id": "7580cc08-b6f3-43a3-af45-5eea2c53aa44",
        "amount": amount,  # Amount in Tomans (or Rials, specify with 'currency')
        "authority": authority
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    print(res.json())
    return res.json()


