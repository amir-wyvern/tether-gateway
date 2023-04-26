# If you intend to run the file independently (you do not intend to run with Docker), remove the section from the comment
# ======================
# import sys
# sys.path.append('../')
# ======================

from db import db_config
from db.database import get_db
from db.db_user import increase_balance
from db.db_main_account import get_deposit_address
from db.models import DepositHistoryStatus
from db.db_deposit import (
    get_deposit_history_by_tx_hash,
    get_deposit_history_by_user_id,
    update_deposit_history_by_request_id, 
    get_deposit_history_by_status
)
from cache.database import get_redis_cache
from cache.cache_session import (
    set_lock_for_user,
    get_status_lock_from_user,
    unlock_user,
    get_status_lock_from_tx_hash,
    set_lock_for_tx_hash,
    unlock_tx_hash
)

from celery_tasks.tasks import DepositCeleryTask 
from celery_tasks.utils import create_worker_from
from schemas import DepositHistoryModelForUpdateDataBase

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import  TransactionNotFound

import json
from dotenv import dotenv_values
from datetime import datetime, timedelta
import logging
import os

if not os.path.exists('logs') :
    os.mkdir('logs')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler to show logs on terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler to save logs to a file
file_handler = logging.FileHandler('logs/deposit_service.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


CONFIG = dotenv_values(".env")

TRANSFER_HASH = CONFIG['TRANSFER_HASH']
REQUEST_EXPIRE_TIME = timedelta(minutes= int(CONFIG['REQUEST_EXPIRE_TIME']))
TX_EXPIRE_TIME = timedelta(minutes= int(CONFIG['TX_EXPIRE_TIME']))

def safe_financial(func):
  
    def wrapper(*args, **kwargs):

        if args[1] == 'check_deposit_request':
            DepositCeleryTaskImpl.check_deposit_requests()
            return
        
        user_id = args[1]['user_id']
        tx_hash = args[1]['tx_hash']
        db = get_redis_cache().__next__()

        safe_lock_user = get_status_lock_from_user(user_id, db) 
        logger.debug(f'cache_session > get_status_lock_from_user > response [user_id: {user_id} -result: {safe_lock_user}]')

        safe_lock_tx_hash = get_status_lock_from_tx_hash(tx_hash, db) 
        logger.debug(f'cache_session > get_status_lock_from_tx_hash > response [user_id: {user_id} -result: {safe_lock_tx_hash}]')

        if safe_lock_user == 'True':
            #send again to celery queue
            arg = args[1]
            logger.debug(f'Send again to celery queue [arg: {arg}]')
            deposit_worker.apply_async(args=(arg,), countdown=15)
            return
        
        if safe_lock_tx_hash == 'True':
            #send again to celery queue
            arg = args[1]
            logger.debug(f'Send again to celery queue [arg: {arg}]')
            deposit_worker.apply_async(args=(arg,), countdown=15)
            return
        
        resp = set_lock_for_user(user_id, db)
        logger.debug(f'cache_session > set_lock_for_user > response [user_id: {user_id} -result: {resp}]')

        resp = set_lock_for_tx_hash(tx_hash, db)
        logger.debug(f'cache_session > set_lock_for_tx_hash > response [user_id: {user_id} -result: {resp}]')

        try :
            func(*args, **kwargs)

        except Exception as e:
            logger.error(f'Exception [user_id: {user_id} -exception: {e}]')

        resp = unlock_user(user_id, db)
        logger.debug(f'cache_session > unlock_user > response [user_id: {user_id} -result: {resp}]')
        
        resp = unlock_tx_hash(tx_hash, db)
        logger.debug(f'cache_session > unlock_tx_hash > response [user_id: {user_id} -result: {resp}]')

    return wrapper

class Contract:

    def __init__(self) -> None:

        logger.debug('Contract class is initialing...')
        self.w3 = Web3(Web3.HTTPProvider(CONFIG["PROVIDER_1"]))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        abi = CONFIG["ABI"]
        abi = abi.replace('\'', '"')
        abi = json.loads(abi)
        self.tether = self.w3.eth.contract(address= CONFIG["CONTRACT"], abi= abi)
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

    def get_tx_time(self, blockNumber) -> datetime:

        logger.debug(f'call get_tx_time [{blockNumber}]')

        failed_count_of_req = 0
        while True:
            
            try:
                timestamp = self.w3.eth.get_block(blockNumber).timestamp
                logger.debug(f'get_tx_time > response [blockNumber: {blockNumber} -time: {timestamp}]')
                return datetime.fromtimestamp(timestamp)

            except TransactionNotFound as e:
                #send notifaction is faild
                logger.debug(f'get_tx_time > TransactionNotFound [blockNumber: {blockNumber}]')
                return False

            except Exception as e:
                logger.debug(f'get_tx_time > Exception [blockNumber: {blockNumber} -exception: {e}]')
                if failed_count_of_req >= 3:
                    logger.warning(f'get_tx_time > Exception > count > 3 [blockNumber: {blockNumber} -exception: {e}]')
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
            # NOTE : dont need the save to database , coz beat celery check it and , in this section we haven't yet request_id 
            logger.info(f'deposit is locked [user_id: {user_id} -tx_hash: {tx_hash}]')
            return
            
        no_check_deposit_requests = get_deposit_history_by_user_id(user_id, db, DepositHistoryStatus.WAITING)
        logger.debug(f'db_deposit > get_deposit_history_by_user_id > response [user_id: {user_id} -result:{len(no_check_deposit_requests) * "*"}')

        deposit_requests = []
        for request in no_check_deposit_requests:
            if datetime.now() - request.request_time < REQUEST_EXPIRE_TIME:
                deposit_requests.append(request)

        if deposit_requests == []:
            # send to notifaction
            # NOTE : dont need the save to the database , coz beat celery check it and , in this section we haven't yet request_id 
            logger.info(f'The user have no deposit request  [user_id: {user_id} -tx_hash: {tx_hash}')
            return
        
        old_tx_hash = get_deposit_history_by_tx_hash(tx_hash, db, status= DepositHistoryStatus.SUCCESS)
        logger.debug(f'db_deposit > get_deposit_history_by_tx_hash > response [user_id: {user_id} -tx_hash: {tx_hash} -result: {old_tx_hash is not None}')
        
        if len(old_tx_hash) > 0:
            # send to notifaction
            # NOTE : dont need the save to the database , coz beat celery check it and , in this section we haven't yet request_id 
            logger.info(f'The tx hash is aleady registerd [user_id: {user_id} -tx_hash: {tx_hash}]')
            return
        
        receipt = self.contract.tx_receipt(tx_hash)

        if not receipt :
            logger.info(f'The receipt of tx hash is None [user_id: {user_id} -tx_hash: {tx_hash}]')
            # send to notifaction
            # NOTE : dont need the save to the database , coz beat celery check it and , in this section we haven't yet request_id 
            return
        
        if receipt['status'] == 0 : 
            # send to notifaction
            # NOTE : dont need the save to the database , coz beat celery check it and , in this section we haven't yet request_id 
            logger.info(f'The transaction is Failed [user_id: {user_id} -tx_hash: {tx_hash}]')
            return
        
        block_timestamp = self.contract.get_tx_time(receipt['blockNumber'])

        if datetime.now() - block_timestamp > TX_EXPIRE_TIME :
            # send to notifaction
            # NOTE : dont need the save to the database , coz beat celery check it and , in this section we haven't yet request_id 
            logger.info(f'A long time has passed since the transaction and it is not accepted [user_id: {user_id} -tx_hash: {tx_hash} -timedelta: {datetime.now() - block_timestamp }]')
            return

        state = False
        for log in receipt['logs']:

            if 'address' in log and \
                log.address == self.contract.tether.address and \
                log.topics[0].hex() == TRANSFER_HASH:
                
                from_address=  Contract.to_check_sum_address(log.topics[1].hex())
                to_address = Contract.to_check_sum_address(log.topics[2].hex())
                if to_address != Contract.to_check_sum_address( get_deposit_address(db)):
                    
                    logger.info(f'The to_address of transaction is not match with to deposit address [user_id: {user_id} -tx_hash: {tx_hash}] ')
                    break

                value = round(int(log.data, 16) / 10 **18, 5)
                state = True

                logger.debug(f'The transaction info > [user_id: {user_id} -tx_hash: {tx_hash} -value: {value} -from_address: {from_address}] ')
                
                break
            
        if state == False:
            # send to notification
            # NOTE : dont need the save to the database , coz beat celery check it and , in this section we haven't yet request_id 
            logger.info(f'The transaction is not valid [user_id: {user_id} -tx_hash: {tx_hash}]')
            return
        
        new_data = {
            'tx_hash': tx_hash,
            'from_address': from_address,
            'error_message': None
        }

        deposit_status = False
        tmp_request_id = None

        for request in deposit_requests:
            
            if request.request_time < block_timestamp and round(request.value, 2) == round(value, 2):

                tmp_request_id = request.request_id
                try:
                    
                    new_data.update({'status': DepositHistoryStatus.SUCCESS, 'processingـcompletionـtime': datetime.now()})

                    increase_balance(request.user_id, value, db, commit=False)
                    update_deposit_history_by_request_id(request.request_id, DepositHistoryModelForUpdateDataBase(**new_data), db, commit=False)
                    db.commit()
                    logger.info(f'Depoist Successfull [request_id: {request.request_id} -user_id: {user_id} -value: {value} -tx_hash: {tx_hash}]')

                    deposit_status = True

                except Exception as e :
                    logger.error(f'Rollback in saving tx [request_id: {request.request_id} ,exception: {e} -user_id: {user_id} -data: {new_data}]')
                    db.rollback()
                    
                    new_data.update({'error_message': f'RollBack [{e}]'})

                break

        if deposit_status == False:
            logger.info(f'The value transaction is not match with any of deposit requests [user_id: {user_id} -tx_hash: {tx_hash}]')

            if tmp_request_id:
                error_message = 'The value transaction is not match with any of deposit requests'
                data = {
                    'tx_hash': tx_hash,
                    'from_address': from_address ,
                    'status': DepositHistoryStatus.FAILED,
                    'error_message': error_message if new_data['error_message'] == None else new_data['error_message'],
                    'processingـcompletionـtime': datetime.now()
                }
                update_deposit_history_by_request_id(tmp_request_id, DepositHistoryModelForUpdateDataBase(**data), db)

        
    @staticmethod
    def check_deposit_requests():
        
        logger.debug('call check_deposit_requests')

        db = get_db().__next__()
        
        ls_requests = get_deposit_history_by_status(DepositHistoryStatus.WAITING, db)
        logger.debug(f'db_deposit > get_deposit_history_by_status > response [status: {DepositHistoryStatus.WAITING} -count: {len(ls_requests)}]')
        
        try:
            for request in ls_requests:

                if datetime.now() - request.request_time > REQUEST_EXPIRE_TIME:
                    new_data = {
                        'error_message': 'the request has expired',
                        'status': DepositHistoryStatus.FAILED,
                        'processingـcompletionـtime': datetime.now()
                    }
                    update_deposit_history_by_request_id(request.request_id, DepositHistoryModelForUpdateDataBase(**new_data), db, commit=False)

            db.commit()
            logger.debug(f'check_deposit_requests is Done!')

        except Exception as e :
            logger.critical(f'Rollback in update_status_by_request_id [exception: {e}]')
            db.rollback()



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

