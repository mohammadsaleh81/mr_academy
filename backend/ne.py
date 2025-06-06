import json

import requests
from datetime import datetime, timedelta
import time

import pytz

def send_sms(phone_number, otp):
    headers = {
        'accept': 'application/json',
        'apikey': 'OWYxMTZkZDUtOTY5Ni00NWZiLTllNGYtMjJjYzZlYTQ0ODk2NTczNDU5MDUwZWU1YjkyYjRkY2QyM2VhNTUwZWU4ZjI=',
        'Content-Type': 'application/json',
    }
    text = "به آکادمی مسترنردیر خوش آمدید کد تایید شما برای ورورد {}".format(otp)
    tehran_tz = pytz.timezone('Asia/Tehran')

    now = datetime.now(tehran_tz)
    send = now
    json_data = {
        'recipient': [
            phone_number,
        ],
        'sender': '+983000505',
        # 'time': str(send),
        'message':text,
    }

    response = requests.post('https://api2.ippanel.com/api/v1/sms/send/webservice/single', headers=headers, json=json_data)
    print(response.text)





send_sms("+989352554850", "12345")

# time.sleep(10)
#
# headers = {
#     'accept': 'application/json',
#     'apikey': 'OWYxMTZkZDUtOTY5Ni00NWZiLTllNGYtMjJjYzZlYTQ0ODk2NTczNDU5MDUwZWU1YjkyYjRkY2QyM2VhNTUwZWU4ZjI=',
#     'Content-Type': 'application/json',
# }
# box = "https://api2.ippanel.com/api/v1/sms/message/all?page=1&per_page=100"
# res = requests.get(box, headers=headers)
# data = res.json()
# with open("sms_log.json", 'w') as f:
#     j = json.dumps(data, indent=4, ensure_ascii=False)
#     f.write(j)




