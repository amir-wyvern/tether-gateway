from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base() 

sessionlocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    session = sessionlocal()
    try:
        yield session
    finally:
        session.close()

