from sqlalchemy.orm.session import Session
from db.models import DbProductDb


def get_product_data_by_sku(db: Session, sku: str):
    product_data = db.query(DbProductDb).filter(DbProductDb.sku == sku).first()
    # 에러 핸들 요망
    try:
        pd = product_data.__dict__
        del pd['_sa_instance_state']
    except AttributeError:
        pd = {}

    return pd





