from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:<password>@localhost/exchange'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base() 

sessionlocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    session = sessionlocal()
    try:
        yield session
    finally:
        session.close()








