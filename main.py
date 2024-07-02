import json
from fastapi import FastAPI
import lib.CP as CP
import lib.SS as SS
import lib.IP as IP
import lib.EW as EW
import time
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "LS ORDER DOWN"}


@app.get("/get_total_order")
async def get_total_order():
    start = time.time()
    # cp = await CP.get_all()
    ss = await SS.get_all()
    ip = await IP.get_all()
    ew = await EW.get_all()

    # 쿠팡 제외...
    # total = cp + ss + ip + ew
    total = ss + ip + ew

    # 계정, 스토어 분류
    # 앞으로 계정 추가시 계정 이니셜 변경 수요 생길 수 있음

    # 리손
    l_ = {"L": {
        "CP": [o for o in total if o["account"] == "L" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "L" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "L" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "L" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "L" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "L" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "L" and o["store"] == "LO"],
    }}
    # 서전
    s_ = {"S": {
        "CP": [o for o in total if o["account"] == "S" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "S" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "S" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "S" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "S" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "S" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "S" and o["store"] == "LO"],
    }}
    # 오금
    o_ = {"O": {
        "CP": [o for o in total if o["account"] == "O" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "O" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "O" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "O" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "O" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "O" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "O" and o["store"] == "LO"],
    }}
    # 은동
    e_ = {"E": {
        "CP": [o for o in total if o["account"] == "E" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "E" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "E" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "E" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "E" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "E" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "E" and o["store"] == "LO"],
    }}
    # 동반
    db_ = {"DB": {
        "CP": [o for o in total if o["account"] == "DB" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "DB" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "DB" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "DB" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "DB" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "DB" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "DB" and o["store"] == "LO"],
    }}

       # 동구
    dg_ = {"DG": {
        "CP": [o for o in total if o["account"] == "DG" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "DG" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "DG" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "DG" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "DG" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "DG" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "DG" and o["store"] == "LO"],
    }}

       # 준승
    js_ = {"DB": {
        "CP": [o for o in total if o["account"] == "JS" and o["store"] == "CP"],
        "SS": [o for o in total if o["account"] == "JS" and o["store"] == "SS"],
        "IP": [o for o in total if o["account"] == "JS" and o["store"] == "IP"],
        "ST": [o for o in total if o["account"] == "JS" and o["store"] == "ST"],
        "AU": [o for o in total if o["account"] == "JS" and o["store"] == "AU"],
        "GM": [o for o in total if o["account"] == "JS" and o["store"] == "GM"],
        "LO": [o for o in total if o["account"] == "JS" and o["store"] == "LO"],
    }}

    # 총 주문
    res = [l_, s_, o_, e_, db_, dg_, js_]
    end = time.time()

    print(f"총 작업 {round(end - start, 5)} 초 소요")

    return len(total), res


@app.get("/test")
async def test():
    client = httpx.AsyncClient()
    config = json.loads(os.environ.get("ss_config"))
    t = await SS.get_token(**config, client=client)
    return t
