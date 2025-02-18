from requests.adapters import HTTPAdapter
import ssl


# ssl downgrade
class CustomHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers("AES256-SHA")  # 서버에서 지원하는 스위트로 변경
        kwargs["ssl_context"] = context
        return super(CustomHttpAdapter, self).init_poolmanager(*args, **kwargs)


def gen_order_form():
    return {
            "store": None,
            "account": None,
            "sku": None,
            "vendorItemName": None,
            "vendorItemId": None,
            "orderId": None,
            "shippingCount": None,
            "totalPrice": None,
            "orderer": None,
            "receiver": None,
            "personalCustomsClearanceCode": None,
            "ordererPhoneNumber": None,
            "receiverPhoneNumber": None,
            "post_code": None,
            "address": None,
            "message": None,
            "orderedAt": None,
            "note1": "",
            "note2": "",
            "slId": None
    }


def trans_store_code(f_name: str):
    if f_name == "인터파크":
        return "IP"
    elif "옥션" in f_name:
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


def trans_account_code(f_name: str):
    if "ogtrading" in f_name:
        return "O"
    # elif "sejeon99" in f_name or "sejeon88" in f_name:
    #     return "S"
    elif "lstraadi" in f_name:
        return "L"
    # elif "eundon99" in f_name or "eundon88" in f_name:
    #     return "E"
    elif "dongban99" in f_name:
        return "B"
    elif "dgtrade99" in f_name:
        return "G"
    elif "jstrade99" in f_name:
        return "J"
