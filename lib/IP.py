import json
import httpx
from datetime import datetime, timedelta
import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.7"
}


async def ip_order_cnt(login_id, login_pwd, account):
    client = httpx.AsyncClient(timeout=2, verify=False)
    client.headers = HEADERS

    body = {
        "loginTgt": "INPK",
        "isProcess": "0",
        "loginId": login_id,
        "loginPwd": login_pwd
    }
    # 오후 1시정도 부터 인터 파크 접속이 불안정 한데에 따른 에러
    try:
        login_and_get_session = await client.post("https://seller.interpark.com/login/process", data=body)
    except httpx.ReadTimeout:
        print("Time Out...")
        return [], account
    except TimeoutError:
        print("Time Out...")
        return [], account

    now = datetime.now()
    before_date = now - timedelta(days=5)

    start_date = before_date.strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")
    page = 1
    size = 30

    url = f"https://seller.interpark.com/api/orders/acknowledge?orderSendStep=acknowledge&orderStatus=50&" \
          f"detailedSearchType=&detailedSearchValue=&searchPeriodType=orderDate&" \
          f"startDate={start_date}T15%3A00%3A00Z&endDate={end_date}T14%3A59%3A00Z&page={page}&size={size}"
    try:
        res = await client.get(url=url)
    except httpx.ReadTimeout:
        print("Time Out...")
        return [], account
    except TimeoutError:
        print("Time Out...")
        return [], account

    try:
        data = json.loads(res.text)
        data = data["data"]
    except json.decoder.JSONDecodeError:
        data = "ERROR!!\n ** CHECK OUT YOUR COOKIES $ PAYLOADS **"
        return [], account

    ip_res = data["orders"]

    return ip_res, account


async def get_all():
    ip_configs = json.loads(os.environ.get("ip_configs"))
    responses = await asyncio.gather(*[ip_order_cnt(**config) for config in ip_configs])

    total = []

    for orders, account in responses:
        for order in orders:
            order_data = {
                "store": "IP",
                "account": account,
                "sku": order["externalParentPrdNo"],
                "vendorItemName": order["prdNm"],
                "vendorItemId": order["prdNo"],
                "orderId": order["ordclmNo"],
                "shippingCount": order["ordCnt"],
                "totalPrice": order["totalPrice"],
                "orderer": order["ordNm"],
                "receiver": order["rcvrNm"],
                "personalCustomsClearanceCode": order["residentNo"],
                "ordererPhoneNumber": order["ordMpno"]
            }
            total.append(order_data)

    return total

# if __name__ == '__main__':
#     start = time.time()
#     res_ = asyncio.run(get_all())
#     end = time.time()
#
#     print(res_)
#     print(f"{round(end - start, 5)} 초 소요")
