import asyncio
import pprint
import ssl
import hashlib
import httpx
from parsel import Selector
from datetime import datetime, timedelta
from lib.etc import gen_order_form, trans_store_code, trans_account_code
import re
from dotenv import load_dotenv
import json
import os


load_dotenv()


CONTEXT = ssl.create_default_context()
CONTEXT.set_ciphers("DEFAULT:@SECLEVEL=1")


class ShopLinker(httpx.AsyncClient):
    def __init__(self, user_id, password):
        super().__init__(verify=CONTEXT)
        self.user_id = user_id
        self.password = password

        self.login_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "ad2.shoplinker.co.kr",
            "Origin": "https://ad2.shoplinker.co.kr",
            "Priority": "u=0,i",
            "Referer": "https://ad2.shoplinker.co.kr/index.php",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/134.0",
            # "x-requested-with": "XMLHttpRequest"
        }

        self.nor_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "ad2.shoplinker.co.kr",
            "Origin": "https://ad2.shoplinker.co.kr",
            "Priority": "u=4",
            "Referer": "https://ad2.shoplinker.co.kr",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/134.0",
        }

    async def login(self):
        t_url = "https://ad2.shoplinker.co.kr/index.php"

        encode_password = self.password.encode()
        sha256_hash = hashlib.sha256()
        sha256_hash.update(encode_password)
        hash_result = sha256_hash.hexdigest()

        form_data = {
            "mode": "login",
            "return_url": "",
            "user_id": self.user_id,
            "login_mode_ez": "Y",
            "passwords": "",
            "pwd_encypt": hash_result,
            "pwd_encypt2": ""
        }

        res = await self.post(t_url, data=form_data, headers=self.login_headers)

        if '_TRK_ISLOGIN="Y"' in res.text:
            return True
        else:
            return False

    async def get_new_order(self):
        t_url = "http://ad2.shoplinker.co.kr/admin/order/order_confirm_proc"

        st_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        la_date = datetime.now().strftime("%Y-%m-%d")

        form_data = {
            "excel_order_type": None,
            "start": None,
            "job": None,
            "mode": "search",
            "set_change": None,
            "set_change_chk": None,
            "invoice_urs": None,
            "is_courier_cnt": 0,
            "is_courier_addr_cnt": 0,
            "date_strss": "register_date",
            "st_date": st_date,
            "la_date": la_date,
            "mall_id": None,
            "autoen_b2b_site": None,
            "autoen_b2c_site": None,
            "gia_site": None,
            "blue_site": None,
            "mall_user_id": None,
            "delivery_sch_name": None,
            "customer_id": "a0027858",
            "sort_field": "register_date",
            "sort": "desc",
            "company_scale": 25,
            "delivery_status2": "001",
            "song_yn": None,
            "pro_no_yn": None,
            "supply_id_chk": None,
            "bae_type_chk": None,
            "err_msg": None,
            "send_status": None,
            "matching_status": None,
            "clame_yn": None,
            "user_name_str": None,
            "receive_str": None,
            "tel_no_str": None,
            "cel_no_str": None,
            "search_field": "user_name",
            "search_str": None,
            "mall_no_chk": None
        }

        res = await self.post(t_url, data=form_data, headers=self.nor_headers)

        sel = Selector(res.text)
        order_rows = sel.xpath("//table[@id='tbl_2']/tbody/tr").getall()

        order_result = []

        for row in order_rows:
            of = gen_order_form()
            sel_r = Selector(row)

            # 샵링커 주문 번호
            of["slId"] = sel_r.xpath("//td[4]/a/text()").get()
            # 스토어 주문 번호
            of["orderId"] = sel_r.xpath("//td[4]/br/following-sibling::text()").get().strip()
            # 스토어
            of["store"] = trans_store_code(sel_r.xpath("//td[5]/img/@alt").get())
            # 계정 정보
            of["account"] = trans_account_code(sel_r.xpath("//td[6]/span/@title").get())
            # 고객사 상품 관리 코드
            of["sku"] = sel_r.xpath("//td[7]/span[2]/text()").get().strip()\
                .replace("(", "")\
                .replace(")", "")
            # 상품명
            of["vendorItemName"] = sel_r.xpath("//td[7]/a[2]/text()").get().strip()\
                if sel_r.xpath("//td[7]/a[2]/text()").get()\
                else sel_r.xpath("//td[7]/a[1]/text()").get().strip()
            # 총 주문액
            of["totalPrice"] = int(sel_r.xpath("//td[12]/br[1]/following-sibling::text()").get().strip().replace(",", ""))
            # 총 주문 개수
            of["shippingCount"] = sel_r.xpath("//td[12]/b/text()").get()
            # 주문자
            of["orderer"] = sel_r.xpath("//td[9]/span/text()").get()
            # 수취인
            of["receiver"] = sel_r.xpath("//td[9]/br[1]/following-sibling::text()").get().strip()
            # 수취인 전화 번호
            of["receiverPhoneNumber"] = sel_r.xpath("//td[9]/br[2]/following-sibling::text()").get().strip()

            order_result.append(of)

        # == 병렬 처리 ==
        responses = await asyncio.gather(*[
            self.get(f"https://ad2.shoplinker.co.kr/admin/order/order_confirm_proc?do=order_basic&id={o['slId']}", headers=self.nor_headers) for o in order_result]
                                )
        # 팝업 페이지 를 통한 consolidation 데이터 수집
        for o, r in zip(order_result, responses):
            sel_c = Selector(r.text)

            # 주문자 번호
            o['ordererPhoneNumber'] = sel_c.xpath("//table[has-class('tbl_row_01')][1]/tbody/tr[3]/td[3]/text()").get()\
                .strip()
            # 수취인 개인 통관 부호
            o['personalCustomsClearanceCode'] = sel_c.xpath("//table[has-class('tbl_row_01')][2]/tbody/tr[4]/td/text()").get()
            # 스토어 ** 상품 ** 번호
            o['vendorItemId'] = sel_c.xpath("//tr[@id='order_list']/td/div/span/text()").get()\
                .strip() \
                .replace("[", "")\
                .replace("]", "")

            # 주소 수집
            full_address = sel_c.xpath("//table[has-class('tbl_row_01')][2]/tbody/tr[2]/td/text()").get()
            post_code = re.search(r'\[(.*?)]', full_address).group(1).strip()
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
            # *** 주소 형식 변경시 대응 필요 ***
            address = full_address.split("]")[1].strip()
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

            o['post_code'] = post_code
            o['address'] = address

            o['orderedAt'] = sel_c.xpath("//table[has-class('tbl_row_01')][3]/tbody/tr[1]/td[2]/text()").get()\
                .strip()

        return order_result


async def get_all():
    sl_config = json.loads(os.environ.get("sl_config"))

    sl = ShopLinker(**sl_config)
    await sl.login()

    total = await sl.get_new_order()

    return total

if __name__ == '__main__':
    r = asyncio.run(get_all())
    pprint.pprint(r)


