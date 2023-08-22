import asyncio
import json
import bcrypt
import pybase64
import time
import urllib.parse
import urllib.request
import httpx
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


async def get_token(client_id, client_secret, client: httpx.AsyncClient):
    timestamp = str(int(time.time() * 1000))
    password = client_id + "_" + timestamp

    # bcrypt 해싱
    hashed = bcrypt.hashpw(password.encode('utf-8'), client_secret.encode('utf-8'))
    # base64 인코딩
    client_secret_sign = pybase64.standard_b64encode(hashed).decode('utf-8')

    _data = {
        "client_id": client_id,
        "timestamp": timestamp,
        "client_secret_sign": client_secret_sign,
        "grant_type": "client_credentials",
        "type": "SELF"
    }

    query = urllib.parse.urlencode(_data)
    url = 'https://api.commerce.naver.com/external/v1/oauth2/token?' + query
    res = await client.post(url)
    res_data = json.loads(res.text)

    if 'access_token' in res_data:
        token = res_data['access_token']
        return str(token)
    else:
        print('토큰 요청 실패')


async def ss_order_cnt(client_id, client_secret, account):

    client = httpx.AsyncClient()
    token = await get_token(client_id, client_secret, client)
    url = 'https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/last-changed-statuses'
    headers = {'Authorization': token}

    now = datetime.now()
    before_date = now - timedelta(days=1)

    before_iso_format = before_date.astimezone().isoformat()

    params = {
        "lastChangedFrom": before_iso_format,
        "lastChangedType": "PAYED"
    }

    res = await client.get(url=url, headers=headers, params=params)
    res_data = json.loads(res.text)

    if 'data' not in res_data:
        res_data = []
        return res_data, account
    else:
        res_data = res_data["data"]["lastChangeStatuses"]
        product_order_ids = [order["productOrderId"] for order in res_data]

        data = await ss_order_detail(product_order_ids, token, client)

        return data, account


async def ss_order_detail(ids: list, token, client: httpx.AsyncClient):
    headers_q = {
        'Authorization': token,
    }

    url_q = "https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/query"

    res_q = await client.post(url=url_q, headers=headers_q, json={"productOrderIds": ids})
    res_q = json.loads(res_q.text)
    data = res_q["data"]
    return data


async def get_all():
    ss_configs = json.loads(os.environ.get("ss_configs"))
    responses = await asyncio.gather(*[ss_order_cnt(**config) for config in ss_configs])

    total = []

    for orders, account in responses:
        for order in orders:
            if order["productOrder"]["placeOrderStatus"] == "OK":
                pass
            else:
                order_data = {
                    "store": "SS",
                    "account": account,
                    "sku": order["productOrder"]["sellerProductCode"],
                    "vendorItemName": order["productOrder"]["productName"],
                    "vendorItemId": order["productOrder"]["productId"],
                    "orderId": order["productOrder"]["productOrderId"],
                    "shippingCount": order["productOrder"]["quantity"],
                    "totalPrice": order["productOrder"]["totalPaymentAmount"],
                    "orderer": order["order"]["ordererName"],
                    "receiver": order["productOrder"]["shippingAddress"]["name"],
                    "personalCustomsClearanceCode": order["productOrder"]["individualCustomUniqueCode"],
                    "ordererPhoneNumber": order["productOrder"]["shippingAddress"]["tel1"]
                }
                total.append(order_data)

    return total

if __name__ == '__main__':
    start = time.time()
    res_ = asyncio.run(get_all())
    end = time.time()

    print(res_)
    print(f"{round(end - start, 5)} 초 소요")

