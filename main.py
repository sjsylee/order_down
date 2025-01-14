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
    stores = ["CP", "SS", "ST", "AU", "GM", "LO"]
    accounts = ["L", "J", "O", "B", "G"]

    res = []

    for acct in accounts:
        r_d = {f"{acct}": {}}
        for store in stores:
            r_d[f"{acct}"][store] = \
                [{**o, **db_product_db.get_product_data_by_sku(db, o['sku'])} for o in total if o["account"] == acct and o["store"] == store]

        res.append(r_d)

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
