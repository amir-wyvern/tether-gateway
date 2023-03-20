from fastapi import FastAPI

from router import (
    user,
    deposit,
    withdraw,
    transfer,
    auth
)
from db import models, db_config, db_main_account
from db.database import engine, get_db
from dotenv import dotenv_values
from pathlib import Path
from schemas import InitMainAccount

dotenv_path = Path('.env')
config = dotenv_values(".env")

description = """
This api allows you to create a payment gateway on the blockchain platform. 🚀

## Items

* Deposit
* Withdraw
* Local Transfer 

## Users

You will be able to:

* **Create users** 
* **Read users** 
* **Edit users** 
"""

app = FastAPI(    
    title="Tether-GateWay",
    description=description,
    version="0.0.1",
    contact={
        "name": "WyVern",
        "email": "amirhosein_wyvern@yahoo.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },) 

app.include_router(user.router)
app.include_router(deposit.router)
app.include_router(withdraw.router)
app.include_router(transfer.router)
app.include_router(auth.router)

models.Base.metadata.create_all(engine)
db_config.init_table(get_db().__next__()) 

main_account = db_main_account.get_deposit_address(get_db().__next__()) 

if main_account is None:

    data = {
        'deposit_address': config['DEPOSIT_ADDRESS'],
        'withdraw_address': config['WITHDRAW_ADDRESS'],
        'p_withdraw': config['ENCODED_WITHDRAW_PRIVATE_KEY']
    }

    db_main_account.init_table(InitMainAccount(**data), get_db().__next__())
