import asyncio
import httpx
import json
from parsel import Selector
import re
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.7"
}


def trans_account_code(f_name: str):
    if "ogtrading" in f_name:
        return "O"
    elif "sejeon99" in f_name or "sejeon88" in f_name:
        return "S"
    elif "lstraadi" in f_name:
        return "L"
    elif "eundon99" in f_name or "eundon88" in f_name:
        return "E"
    elif "dongban99" in f_name:
        return "B"
    elif "dgtrading" in f_name:
        return "G"
    elif "jstrade99" in f_name:
        return "J"


def trans_store_code(f_name: str):
    if f_name == "인터파크":
        return "IP"
    elif f_name == "옥션":
        return "AU"
    elif f_name == "지마켓":
        return "GM"
    elif f_name == "롯데온":
        return "LO"
    elif f_name == "11번가":
        return "ST"
    elif f_name == "쿠팡":
        return "CP"
    elif f_name == "스마트스토어":
        return "SS"


# 리스트 분할
def divide_chunks(m_list, n):
    for i in range(0, len(m_list), n):
        yield m_list[i:i + n]


async def get_all():
    client = httpx.AsyncClient(verify=False, timeout=None)
    client.headers = HEADERS

    ew_config = json.loads(os.environ.get("ew_config"))
    await client.post("http://mgr.easywinner.co.kr/login", data=ew_config)

    order_data = await client.get(url="https://mgr.easywinner.co.kr/admin/order?do=list_content")
    json_data = json.loads(order_data.text)

    # 테이블 데이터 가져 오기
    sel = Selector(json_data["content"])
    rows = sel.xpath("//tbody/tr").getall()
    rows = [t for t in rows if "발주확인" not in t]

    all_td = []
    sku_list = []
    store_list = []
    title_list = []
    prod_num_list = []
    store_order_id_list = []
    ew_id_list = []
    order_id_list = []

    for row in rows:
        # Row 데이터 추출
        sel_r = Selector(row)
        t_data = sel_r.xpath("//td/text()").getall()
        t_data = [t.replace("\n", "").strip() for t in t_data]
        t_data = list(filter(lambda data: data != "", t_data))
        all_td.append(t_data)
        # print(t_data)

        # SKU 추출
        row_sku = sel_r.xpath("//td/div/text()").getall()
        row_sku = [t.replace("\n", "").strip() for t in row_sku]
        row_sku = list(filter(lambda data: data != "", row_sku))
        try:
            sku = re.search(r'\((.*?)\)', row_sku[-1]).group(1)
        except AttributeError:
            # 이지 위너에 SKU 가 없는 경우
            sku = "보관 상품코드 없음"
        sku_list.append(sku)

        # 스토어 정보 추출
        store = sel_r.xpath("//span[has-class('nsl-shop-img')]/img/@alt").get()
        store_list.append(store)
        # print(store)

        # 제목, 상품 번호 추출
        title = sel_r.xpath("//div[has-class('t_left tip')]/@title").getall()[0]
        prod_num = re.search(r'\((.*?)\)', title).group(1)
        prod_num_list.append(prod_num)
        title = title[len(prod_num) + 2:]
        title_list.append(title)

        # 쇼핑몰 주문 번호 추출
        store_order_id = sel_r.xpath("//td/a[has-class('detail_popup')]/text()").getall()[0]
        store_order_id_list.append(store_order_id.strip())
        # print(store_order_id.strip())

        # 이지 위너 id 추출
        ew_id = sel_r.xpath("//input[@name='No[]']/@value").getall()[0]
        ew_id_list.append(ew_id)
        # print(ew_id)

        # 상품 주문 번호
        order_id = sel_r.xpath("//td/a[has-class('detail_popup')]/text()").getall()[0]
        order_id_list.append(order_id.strip())
        # print(order_id.strip())

    customer_id = "s0008454"

    result = []
    for ew_id, store_order_id in zip(ew_id_list, store_order_id_list):
        t_url = f"https://mgr.easywinner.co.kr/admin/order/detail?id={ew_id}" \
                f"&customer_id={customer_id}&order_no={store_order_id}&page=1"
        res = await client.get(url=t_url)
        # print(res.text)
        sel = Selector(res.text)

        table_list = sel.xpath("//table").getall()
        t_table = table_list[1]

        sel = Selector(t_table)
        # t_name = sel.xpath("//tr/th/text()").getall()
        t_data = sel.xpath("//tr/td/text()").getall()
        t_data = [d.strip() for d in t_data]

        del t_data[1]
        del t_data[2]

        # 배송 메세지 가 없는 경우
        if len(t_data) == 4:
            t_data.insert(3, "")

        # 통관 번호, 배송 메세지 가 없는 경우
        if len(t_data) == 3:
            t_data.insert(3, "")
            t_data.insert(4, "")

        orderder_name = t_data[0].split("(")[0].strip()
        try:
            orderer_phone = re.search(r'\((.*?)\)', t_data[0][1:]).group(1).split("/")[1].strip()
        except IndexError:
            orderer_phone = ""
        except AttributeError:
            orderer_phone = ""

        try:
            receiver_phone = re.search(r'\((.*?)\)', t_data[1]).group(1).split("/")[1].strip()
        except IndexError:
            receiver_phone = re.search(r'\((.*?)\)', t_data[1].split(") ")[1]).group(1).split("/")[1].strip()

        per_data = {
            "orderder_name": orderder_name,
            "orderer_phone": orderer_phone,
            "receiver": t_data[1].split("(")[0].strip(),
            "receiver_phone": receiver_phone,
            "post_code": re.search(r'\[(.*?)]', t_data[2]).group(1),
            "address": t_data[2].split("]")[1].strip(),
            "message": t_data[3],
            "customs_num": t_data[4],
            "ew_id": ew_id
        }
        result.append(per_data)

    total = []
    for store, title, prod_num, sku, order_id, td, per in zip(store_list, title_list, prod_num_list, sku_list,
                                                              order_id_list, all_td, result):
        # *************** 오류 처리 ***************
        # print(store)
        # print(title)
        # print(len(td))
        # print(status)
        # ***************

        if store == "인터파크":
            pass
        else:
            if store == "롯데온":
                title = title
            order_data = {
                "store": trans_store_code(store),
                "account": trans_account_code(td[2]),
                "sku": sku,
                "vendorItemName": title,
                "vendorItemId": prod_num,
                "orderId": str(order_id).strip(),
                "shippingCount": int(td[4]),
                "totalPrice": int(td[5].replace(",", "")),
                "orderer": td[3],
                "receiver": td[6],
                "personalCustomsClearanceCode": per["customs_num"],
                "ordererPhoneNumber": td[7],
                "ew_id": per["ew_id"]
            }
            total.append(order_data)

    return total


async def order_confirm(trans_id, m_prd_id):
    client = httpx.AsyncClient(verify=False, timeout=None)
    client.headers = HEADERS
    print(trans_id)
    print(m_prd_id)

    ew_config = json.loads(os.environ.get("ew_config"))
    await client.post("http://mgr.easywinner.co.kr/login", data=ew_config)

    payload = {
        # "_token": "l0PtYsIoyO6xynBanEf303IqOqH1iGYMd0oTvj8M",
        "customer_id": "s0008454",
        "req_url": "http://linkage.easywinner.co.kr/Order/database_job_beaIngChg2.html",
        "work_cls": "order_confirm",
        "index_name": "index_ajax",
        "mode": "search",
        "date_strss": "register_date",
        "st_date": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}",
        "la_date": f"{datetime.now().strftime('%Y-%m-%d')}",
        "fail_st_date": f"{datetime.now().strftime('%Y-%m-%d')}",
        "fail_la_date": f"{datetime.now().strftime('%Y-%m-%d')}",
        "order_fail_page": "N",
        "delivery_status2": "001",
        "search_field": "user_name",
        "sort_field": "register_date",
        "sort": "desc",
        "exl_num": "181335",
        "No[]": trans_id,
        "id[]": trans_id,
        "_delivery_status[]": "001",
        f"old_delivery_status_chg_{trans_id}": "001",
        f"mall_id_{trans_id}": "mall0184",
        f"customer_id_{trans_id}": "s0008454",
        f"mall_product_id_{trans_id}": m_prd_id
    }

    print(payload)

    request_data = await client.post(url="https://mgr.easywinner.co.kr/admin/linker/request_group", data=payload)
    request_data = json.loads(request_data.text)

    print(request_data)

    if request_data["status"] == "ok":
        return True
    else:
        return False


if __name__ == '__main__':
    start = time.time()
    res_ = asyncio.run(order_confirm("1010633651", "6076399606"))
    end = time.time()

    print(res_)
    print(f"{round(end - start, 5)} 초 소요")

