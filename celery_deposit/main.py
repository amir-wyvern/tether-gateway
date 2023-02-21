import sys

sys.path.append('../')

from db import db_config
from db.database import get_db
from db.db_user import increase_balance
from db.db_main_account import get_deposit_address
from db.models import DepositRequestStatus, DepositHistoryStatus
from db.db_deposit_request import (
    get_request_deposit_by_user,
    update_status_by_request_id,
    get_request_deposit_by_status
)
from db.db_deposit_history import (
    create_deposit_history,
    get_history_deposit_by_tx_hash
)
from cache.database import get_redis_cache
from cache.cache_session import (
    set_lock_for_user,
    get_status_lock_from_user,
    unlock_user
)

from celery_tasks.tasks import DepositCeleryTask 
from celery_tasks.utils import create_worker_from
from schemas import DepositHistoryModelForDataBase

from web3 import Web3
from web3.exceptions import  TransactionNotFound

import json
from dotenv import dotenv_values
from datetime import datetime, timedelta
import logging

# logging.basicConfig(level=logging.DEBUG, 
#                     format='%(asctime)s - %(levelname)s | %(message)s')


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler to show logs on terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler to save logs to a file
file_handler = logging.FileHandler('deposit_service.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


config = dotenv_values("celery_deposit/.env")

TRANSFER_HASH = config['TRANSFER_HASH']


def safe_financial(func):
  
    def wrapper(*args, **kwargs):

        if args[1] == 'check_deposit_request':
            DepositCeleryTaskImpl.check_deposit_requests()
            return
        
        user_id = args[1]['user_id']
        db = get_redis_cache().__next__()

        logging.debug(f'cache_session > get_status_lock_from_user > request  [user_id: {user_id}]')
        safe_lock = get_status_lock_from_user(user_id, db) 
        logging.debug(f'cache_session > get_status_lock_from_user > response [user_id: {user_id} -result: {safe_lock}]')

        if safe_lock == 'True':
            #send again to celery queue
            arg = args[1]
            logger.debug(f'Send again to celery queue [arg: {arg}]')
            deposit_worker.apply_async(args=(arg,), countdown=15)
            return
        
        logging.debug(f'cache_session > set_lock_for_user > request  [user_id: {user_id}]')
        resp = set_lock_for_user(user_id, db)
        logging.debug(f'cache_session > set_lock_for_user > response [user_id: {user_id} -result: {resp}]')

        func(*args, **kwargs)

        logging.debug(f'cache_session > unlock_user > request  [user_id: {user_id}]')
        resp = unlock_user(user_id, db)
        logging.debug(f'cache_session > unlock_user > response [user_id: {user_id} -result: {resp}]')

    return wrapper

class Contract:

    def __init__(self) -> None:

        logger.debug('Contract class is initialing...')
        self.w3 = Web3(Web3.HTTPProvider(config["PROVIDER_1"]))
        abi = config["ABI"]
        abi = abi.replace('\'', '"')
        abi = json.loads(abi)
        self.tether = self.w3.eth.contract(address= config["CONTRACT"], abi= abi)
        logger.debug('Contract class is initialed')

    def tx_receipt(self, tx_hash):
        
        logger.debug(f'call tx_receipt [{tx_hash}]')

        failed_count_of_req = 0
        while True:
            
            try:
                receipt = self.w3.eth.getTransactionReceipt(tx_hash)
                logger.debug(f'tx_receipt > response [tx_hash: {tx_hash}]')
                return receipt

            except TransactionNotFound as e:
                #send notifaction is faild
                logger.debug(f'tx_receipt > TransactionNotFound [tx_hash: {tx_hash}]')
                return False

            except Exception as e:
                logger.debug(f'tx_receipt > Exception [tx_hash: {tx_hash} -exception: {e}]')
                if failed_count_of_req >= 3:
                    logger.warning(f'tx_receipt > Exception > count > 3 [tx_hash: {tx_hash}]')
                    return False 
                
                failed_count_of_req += 1

    @staticmethod
    def to_check_sum_address(address):

        return Web3.toChecksumAddress(hex(int(address, 16)))


class DepositCeleryTaskImpl(DepositCeleryTask):

    def __init__(self):

        self.contract = Contract()

    @safe_financial
    def run(self, payload):
        
        logger.debug(f'Receive a task [payload: {payload}]')

        user_id = payload["user_id"]
        tx_hash = payload["tx_hash"]

        db = get_db().__next__()

        config = db_config.get_config(db)
        
        if config.deposit_lock == True:
            # send to notifacion 
            logger.info(f'deposit is locked [user_id: {user_id} -tx_hash: {tx_hash}]')
            return
            
        logger.debug(f'db_deposit_request > get_request_deposit_by_user > request  [user_id: {user_id} -state: {DepositRequestStatus.WAITING}]')
        no_check_deposit_requests = get_request_deposit_by_user(user_id, db, DepositRequestStatus.WAITING)
        logger.debug(f'db_deposit_request > get_request_deposit_by_user > response [user_id: {user_id} -result:{len(no_check_deposit_requests) * "*"}')

        deposit_requests = []
        for request in no_check_deposit_requests:
            if datetime.now() - request.timestamp < timedelta(hours=1):
                deposit_requests.append(request)

        if deposit_requests == []:
            logger.info(f'The user have no deposit request  [user_id: {user_id} -tx_hash: {tx_hash}')
            # send to notifaction
            return
        
        logger.debug(f'db_deposit_request > get_history_deposit_by_tx_hash > request  [user_id: {user_id} -tx_hash: {tx_hash}')
        old_tx_hash = get_history_deposit_by_tx_hash(tx_hash, db)
        logger.debug(f'db_deposit_request > get_history_deposit_by_tx_hash > response [user_id: {user_id} -tx_hash: {tx_hash} -result: {old_tx_hash is not None}')
        
        if old_tx_hash is not None and old_tx_hash.status == DepositHistoryStatus.RECEIVED:
            # send to notifaction
            logger.info(f'The tx hash is aleady registerd [user_id: {user_id} -tx_hash: {tx_hash}]')
            return
        
        receipt = self.contract.tx_receipt(tx_hash)

        if not receipt :
            logger.info(f'The receipt of tx hash is None [user_id: {user_id} -tx_hash: {tx_hash}]')
            # send to notifaction
            return
        
        if receipt['status'] == 0 : 
            logger.info(f'The transaction is Failed [user_id: {user_id} -tx_hash: {tx_hash}]')
            # send to notifaction
            return
        
        
        state = False
        for log in receipt['logs']:

            if 'address' in log and \
                log.address == self.contract.tether.address and \
                log.topics[0].hex() == TRANSFER_HASH:
                
                from_address=  Contract.to_check_sum_address(log.topics[1].hex())
                to_address = Contract.to_check_sum_address(log.topics[2].hex())
                if to_address != Contract.to_check_sum_address( get_deposit_address(db) ):
                    
                    logger.info(f'The to_address of transaction is not match with to deposit address [user_id: {user_id} -tx_hash: {tx_hash}] ')
                    break

                value = round(int(log.data, 16) / 10 **18, 5)
                state = True

                logger.debug(f'The transaction info > [user_id: {user_id} -tx_hash: {tx_hash} -value: {value} -from_address: {from_address}] ')
                
                break
            
        if state == False:
            logger.info(f'The transaction is not valid [user_id: {user_id} -tx_hash: {tx_hash}]')
            # send to notification
            return
        
        deposit_status = False
        for request in deposit_requests:
            if round(request.value, 2) == round(value, 2):
                
                data = {
                    'tx_hash': tx_hash,
                    'request_id': request.request_id,
                    'user_id': user_id,
                    'origin_address': from_address ,
                    'destination_address': to_address,
                    'error_message': '',
                    'status': DepositHistoryStatus.RECEIVED,
                    'value': value,
                    'timestamp': datetime.now()
                }
                
                logger.debug(f'Saving a transaction in deposit history DB [data: {data}]')

                try:
                    increase_balance(request.user_id, value, db, commit=False)
                    create_deposit_history(DepositHistoryModelForDataBase(**data), db, commit=False)
                    update_status_by_request_id(request.request_id, DepositHistoryStatus.RECEIVED, db, commit=False)
                    db.commit()
                    deposit_status = True

                except Exception as e :
                    logger.error(f'Rollback in saving tx [exception: {e} -data: {data}]')
                    db.rollback()
                    raise e

                break

        if deposit_status == False:

            logger.info(f'The value transaction is not match with any of deposit requests [user_id: {user_id} -tx_hash: {tx_hash}]')
        
    @staticmethod
    def check_deposit_requests():
        
        logging.debug('call check_deposit_requests')

        db = get_db().__next__()
        
        logger.debug(f'db_deposit_request > get_request_deposit_by_status > request [status: {DepositRequestStatus.WAITING}]')
        ls_requests = get_request_deposit_by_status(DepositRequestStatus.WAITING, db)
        logger.debug(f'db_deposit_request > get_request_deposit_by_status > response [status: {DepositRequestStatus.WAITING} -count: {len(ls_requests)}]')
        
        try:
            for request in ls_requests:

                if datetime.now() - request.timestamp > timedelta(hours=1):
                    update_status_by_request_id(request.request_id, DepositHistoryStatus.FAILED, db, commit=False)
            
            db.commit()
            logger.debug(f'check_deposit_requests is Done!')

        except Exception as e :
            logger.error(f'Rollback in update_status_by_request_id [exception: {e}]')
            db.rollback()
            raise e



# create celery app
app, deposit_worker = create_worker_from(DepositCeleryTaskImpl)
# _, notifaction_worker = create_worker_from(NotificationCeleryTask)

beat_schedule = {
    'check_deposit_requests_every_five_minute':{
        'task': 'Deposit_celery_task',
        'schedule': timedelta(minutes=5),
        'args': ('check_deposit_request',)
    }
}

app.conf.beat_schedule = beat_schedule


# start worker
if __name__ == '__main__':
    
    app.worker_main()

