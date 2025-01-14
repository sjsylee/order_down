from fastapi import FastAPI, Depends
import lib.SL as SL
import time
from dotenv import load_dotenv
from db.database import get_db
from sqlalchemy.orm.session import Session
from db import db_product_db


load_dotenv()


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "LS ORDER DOWN"}


@app.get("/get_total_order")
async def get_total_order(db: Session = Depends(get_db)):
    start = time.time()
    # *== LEGACY ==*

    # cp = await CP.get_all()
    # ss = await SS.get_all()
    # ip = await IP.get_all()
    # ew = await EW.get_all()

    # 쿠팡, 스마트스토어, 인터파크 제외...
    # total = cp + ss + ip + ew
    # total = ss + ip + ew

    # *======================================================================*

    sl = await SL.get_all()

    total = sl

    # 계정,스토어 분류
    # 앞으로 계정 추가시 계정 이니셜 변경 수요 생길 수 있음

    # 리손
    l_ = {"L": {
        "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "L" and o["store"] == "CP"],
        "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "L" and o["store"] == "SS"],
        "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "L" and o["store"] == "ST"],
        "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "L" and o["store"] == "AU"],
        "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "L" and o["store"] == "GM"],
        "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "L" and o["store"] == "LO"],
    }}

    # 준승
    js_ = {"J": {
        "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "J" and o["store"] == "CP"],
        "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "J" and o["store"] == "SS"],
        "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "J" and o["store"] == "ST"],
        "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "J" and o["store"] == "AU"],
        "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "J" and o["store"] == "GM"],
        "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "J" and o["store"] == "LO"],
    }}

    # ==**== LEGACY ==**==
    # 서전
    # s_ = {"S": {
    #     "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "CP"],
    #     "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "SS"],
    #     "IP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "IP"],
    #     "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "ST"],
    #     "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "AU"],
    #     "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "GM"],
    #     "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "S" and o["store"] == "LO"],
    # }}

    # 오금
    o_ = {"O": {
        "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "O" and o["store"] == "CP"],
        "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "O" and o["store"] == "SS"],
        "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "O" and o["store"] == "ST"],
        "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "O" and o["store"] == "AU"],
        "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "O" and o["store"] == "GM"],
        "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "O" and o["store"] == "LO"],
    }}
    # ==**== LEGACY ==**==
    # 은동
    # e_ = {"E": {
    #     "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "CP"],
    #     "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "SS"],
    #     "IP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "IP"],
    #     "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "ST"],
    #     "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "AU"],
    #     "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "GM"],
    #     "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "E" and o["store"] == "LO"],
    # }}
    # 동반
    db_ = {"B": {
        "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "B" and o["store"] == "CP"],
        "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "B" and o["store"] == "SS"],
        "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "B" and o["store"] == "ST"],
        "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "B" and o["store"] == "AU"],
        "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "B" and o["store"] == "GM"],
        "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "B" and o["store"] == "LO"],
    }}

    # 동구
    dg_ = {"G": {
        "CP": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "G" and o["store"] == "CP"],
        "SS": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "G" and o["store"] == "SS"],
        "ST": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "G" and o["store"] == "ST"],
        "AU": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "G" and o["store"] == "AU"],
        "GM": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "G" and o["store"] == "GM"],
        "LO": [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == "G" and o["store"] == "LO"],
    }}

    # 총 주문
    # res = [l_, s_, o_, e_, db_, dg_, js_]
    res = [l_, js_, o_, db_, dg_]

    end = time.time()

    print(f"총 작업 {round(end - start, 5)} 초 소요")

    return len(total), res


@app.get("/get_monthly_order_data_by_date")
async def get_monthly_order_data_by_date(db: Session = Depends(get_db)):
    return db_product_db.get_monthly_order_data_by_date(db)


@app.get("/get_today_order_data")
async def get_today_order_data(db: Session = Depends(get_db)):
    return db_product_db.get_today_order_data(db)


@app.get("/get_data_by_sku/{sku}")
async def get_data_by_account(sku: str, db: Session = Depends(get_db)):
    return db_product_db.get_monthly_order_data_by_date(db, sku)


# **== LEGACY ==**
# @app.get("/order_confirm/{trans_id}/{m_prd_id}")
# async def order_confirm(trans_id, m_prd_id):
#     ew = await EW.order_confirm(trans_id, m_prd_id)
#     return ew
