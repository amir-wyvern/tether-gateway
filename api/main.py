from fastapi import FastAPI

from router import (
    user,
    deposit,
    withdraw,
    transfer
)
from db import models, db_config
from db.database import engine, get_db
from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

app = FastAPI() 
app.include_router(user.router)
app.include_router(deposit.router)
app.include_router(withdraw.router)
app.include_router(transfer.router)

models.Base.metadata.create_all(engine)
db_config.init_table(get_db().__next__()) 