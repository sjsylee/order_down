import asyncio
import hmac
import hashlib
import urllib.parse
import urllib.request
import ssl
import json
import os
from datetime import datetime, timedelta
import time
import httpx
from dotenv import load_dotenv

load_dotenv()


async def cp_order_cnt(vendor_id, access_key, secret_key, account):
    # 시간, hmac 해싱 과정
    method = "GET"
    os.environ['TZ'] = 'GMT+0'

    # =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=
    datetime_ = time.strftime('%y%m%d') + 'T' + time.strftime('%H%M%S') + 'Z'
    now = datetime.now()
    before_date = now - timedelta(days=2)

    # =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=
    created_at_from = before_date.strftime("%Y-%m-%d")
    created_at_to = now.strftime("%Y-%m-%d")

    # =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=
    path = f"/v2/providers/openapi/apis/api/v4/vendors/{vendor_id}/ordersheets"
    query = urllib.parse.urlencode({"createdAtFrom": created_at_from, "createdAtTo": created_at_to, "status": "ACCEPT"})

    message = datetime_ + method + path + query
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    authorization = "CEA algorithm=HmacSHA256, access-key=" + access_key + ", signed-date=" + datetime_ + ", signature=" + signature

    # ************* SEND THE REQUEST *************
    url = "https://api-gateway.coupang.com" + path + "?%s" % query

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    client = httpx.AsyncClient(verify=ctx)
    client.headers = {
        "Content-type": "application/json;charset=UTF-8",
        "Authorization": authorization
    }

    try:
        resp = await client.get(url=url)
    except httpx.HTTPError as e:
        return e, account
    else:
        data = json.loads(resp.text)
        return data["data"], account


async def get_all():
    cp_configs = json.loads(os.environ.get("cp_configs"))
    responses = await asyncio.gather(*[cp_order_cnt(**config) for config in cp_configs])

    total = []

    for orders, account in responses:
        try:
            for order in orders:
                item = order["orderItems"][0]
                oversea_info = order["overseaShippingInfoDto"]

                order_data = {
                    "store": "CP",
                    "account": account,
                    "sku": item["externalVendorSkuCode"],
                    "vendorItemName": item["vendorItemName"],
                    "vendorItemId": item["productId"],
                    "orderId": order["orderId"],
                    "shippingCount": item["shippingCount"],
                    "totalPrice": item["orderPrice"],
                    "orderer": order["orderer"]["name"],
                    "receiver": order["receiver"]["name"],
                    "personalCustomsClearanceCode": oversea_info["personalCustomsClearanceCode"],
                    "ordererPhoneNumber": oversea_info["ordererPhoneNumber"],
                    "shippingId": order["shipmentBoxId"],
                }

                total.append(order_data)
        except TypeError:
            pass

    return total


if __name__ == '__main__':
    start = time.time()
    res = asyncio.run(get_all())
    end = time.time()

    print(res)
    print(f"{round(end - start, 5)} 초 소요")
