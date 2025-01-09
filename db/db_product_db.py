from sqlalchemy.orm.session import Session
from datetime import datetime, timedelta
from pytz import timezone
from sqlalchemy import func
from db.models import DbProductDb, DbOrderData
from dateutil.relativedelta import relativedelta


def get_product_data_by_sku(db: Session, sku: str):
    product_data = db.query(DbProductDb).filter(DbProductDb.sku == sku).first()
    # 에러 핸들 요망
    try:
        pd = product_data.__dict__
        del pd['_sa_instance_state']
    except AttributeError:
        pd = {}

    return pd


def get_monthly_order_data_by_date(db: Session):
    dt = datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d")
    d = datetime.strptime(dt, "%Y-%m-%d")
    start_of_month = d.replace(day=1)
    end_of_month = (d + relativedelta(months=1)).replace(day=1) - timedelta(days=1)

    order_data = db.query(DbOrderData).filter(DbOrderData.selling_time.between(start_of_month, end_of_month)).all()
    return_data = []

    for d in order_data:
        pd = d.__dict__
        del pd['_sa_instance_state']
        return_data.append(pd)

    return return_data


def get_today_order_data(db: Session):
    date = datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d")
    order_data = db.query(DbOrderData).filter(func.DATE(DbOrderData.selling_time) == date).all()
    return_data = []

    for d in order_data:
        pd = d.__dict__
        del pd['_sa_instance_state']
        return_data.append(pd)

    return return_data







