from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json
import os

load_dotenv()

DB_CONFIG = json.loads(os.environ.get("db_config"))

SQLALCHEMY_DATABASE_URL = f"mariadb+mariadbconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
