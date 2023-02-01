from fastapi import FastAPI, status, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from router import user, deposit
# from auth import authentication
from db import models, db_config
from db.database import engine, get_db
from exceptions import EmailNotValid


app = FastAPI()
app.include_router(user.router)
# app.include_router(deposit.router)


models.Base.metadata.create_all(engine)
db_config.init_table(get_db().__next__())
