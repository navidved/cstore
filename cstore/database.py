import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cstore_sqlite.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
DcBase = declarative_base()
