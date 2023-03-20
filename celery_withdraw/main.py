# If you intend to run the file independently (you do not intend to run with Docker), remove the section from the comment
# ======================
# import sys
# sys.path.append('../')
# ======================

from db.database import get_db
from db import db_config
from db.db_main_account import get_p_withdraw, get_withdraw_address
from db.db_user import get_user, decrease_balance
from db.db_withdraw import (
    update_withdraw_history_by_request_id
)
from celery_tasks.tasks import WithdrawCeleryTask
from celery_tasks.utils import create_worker_from
from schemas import (
    WithdrawHistoryModelForUpdateDataBase,
    WithdrawHistoryStatus,
)

from cache.database import get_redis_cache
from cache.cache_session import (
    set_lock_for_user,
    get_status_lock_from_user,
    unlock_user
)

from web3 import Web3
from celery_withdraw.pk_security import decrypt_private_key

import json
from dotenv import dotenv_values
from datetime import datetime
from getpass import getpass
import logging 
import os

if not os.path.exists('logs') :
    os.mkdir('logs')

ENV = dotenv_values(".env")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler to show logs on terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler to save logs to a file
file_handler = logging.FileHandler('logs/withdraw_service.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def safe_financial(func):
  
    def wrapper(*args, **kwargs):

        user_id = args[1]['user_id']
        request_id = args[1]['request_id']
        db = get_redis_cache().__next__()

        safe_lock = get_status_lock_from_user(user_id, db) 
        logging.debug(f'cache_session > get_status_lock_from_user > response [request_id: {request_id} -user_id: {user_id} -result: {safe_lock}]')

        if safe_lock == 'True':
            #send again to celery queue
            arg = args[1]
            logger.debug(f'Send again to celery queue [arg: {arg}]')
            withdraw_worker.apply_async(args=(arg,), countdown=15)
            return
        
        resp = set_lock_for_user(user_id, db)
        logging.debug(f'cache_session > set_lock_for_user > response [request_id: {request_id} -user_id: {user_id} -result: {resp}]')

        try:
            func(*args, **kwargs)

        except Exception as e:
            logger.error(f'Exception [user_id: {user_id} -exception: {e}]')

        resp = unlock_user(user_id, db)
        logging.debug(f'cache_session > unlock_user > response [request_id: {request_id} -user_id: {user_id} -result: {resp}]')

    return wrapper


class Contract:

    def __init__(self) -> None:

        logger.debug('Contract class is initialing...')
        self.w3 = Web3(Web3.HTTPProvider(ENV["PROVIDER_1"]))
        abi = ENV["ABI"]
        abi = abi.replace('\'', '"')
        abi = json.loads(abi)
        self.tether = self.w3.eth.contract(address= ENV["CONTRACT"], abi= abi)
        self.decimals = self.tether.functions.decimals().call()
        
        logger.debug('Contract class is initialed')


    def send_tx(self, request_id, value, to_address, private_key):

        account = self.w3.eth.account.from_key(private_key)
        failed_count_of_req = 0
        while True:

            try:
                nonce = self.w3.eth.getTransactionCount(account.address)
                logger.debug(f'Contract > send_tx > nonce > response [request_id: {request_id} -nonce: {nonce}]')
                gas_price_wei = self.w3.eth.gasPrice
                chain_id = self.w3.eth.chain_id
                
                value_with_deciamls = int(value * 10** self.decimals)

                tx = self.tether.functions.transfer(to_address, value_with_deciamls).buildTransaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gasPrice': gas_price_wei,
                    'chainId': chain_id,
                })
                

                gas_estimate = self.w3.eth.estimateGas(tx)
                tx.update({'gas': gas_estimate })
                
                logger.debug(f'Contract > send_tx > buildTransaction [request_id: {request_id} -tx: {tx}]')

                signed_tx = account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
                logger.debug(f'Contract > send_tx > send_raw_transaction > response [request_id: {request_id} -tx_hash: {tx_hash}]')

                return self.wait_for_tx_receipt(request_id, tx_hash)
                
            except Exception as e:
                
                logger.debug(f'Contract > send_tx > Exception [request_id: {request_id} -exception: {e}]')
                if failed_count_of_req >= 1:
                    logger.error(f'Contract > send_tx > Exception > count > 1 [request_id: {request_id}]')
                    return None, False ,e 
                
                failed_count_of_req += 1
                
    def wait_for_tx_receipt(self, request_id, tx_hash):

        failed_count_of_req = 0
        while True:
            try:
                
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

                if receipt and receipt['status'] == 1:
                    logger.debug(f'Contract > wait_for_tx_receipt > Transaction succeeded > response [request_id: {request_id} -tx_hash: {tx_hash}]')
                    return tx_hash, True, None

                else:
                    logger.debug(f'Contract > wait_for_tx_receipt > ransaction failed > response [request_id: {request_id} -tx_hash: {tx_hash}]')
                    return tx_hash, False, 'status recepit is False'
            
            except Exception as e:

                if failed_count_of_req >= 1:
                    logger.error(f'Contract > wait_for_tx_receipt > Exception [request_id: {request_id} -exception: {e}]')
                    return tx_hash, False, e
                
                failed_count_of_req += 1
                # NOTE : check  for tx , if tx is timeout and user send again withdraw request , so it's double spending atttack !!!


class WithdrawCeleryTaskImpl(WithdrawCeleryTask):

    def __init__(self):

        self.pk_password = getpass("Enter password for private key: ")
        try :
            db = get_db().__next__()
            encryted_private_key = get_p_withdraw(db)
            decrypt_private_key(encryted_private_key, self.pk_password, ENV['PRIVATE_KEY_SALT'])
            logger.debug('password is correct')
        except:
            logger.debug('password is not correct!')
            exit(0)
        self.contract = Contract()

    @safe_financial
    def run(self, payload):
        
        logger.debug(f'Receive a task [payload: {payload}]')

        request_id = payload["request_id"]
        user_id = payload["user_id"]
        value = payload["value"]
        to_address = payload["to_address"]

        db = get_db().__next__()

        config = db_config.get_config(db)
        logger.debug(f'db_config > get_config > response [request_id: {request_id} -result: {config is not None}]')

        from_address = get_withdraw_address(db)
        logger.debug(f'db_main_account > get_withdraw_address > response [request_id: {request_id} -result: {from_address}]')

        if config.withdraw_lock == True:
            # send to notifacion 
            logger.info(f'withdraw has locked [request_id: {request_id} -user_id: {user_id}]')

            new_data = {
                'status': WithdrawHistoryStatus.FAILED,
                'error_message': 'withdraw has locked',
                'processingـcompletionـtime': datetime.now(),
            }
            update_withdraw_history_by_request_id(request_id, WithdrawHistoryModelForUpdateDataBase(**new_data), db)
            return
        
        user_data = get_user(user_id, db)
        logger.debug(f'db_user > get_user > response [request_id: {request_id} -result: {user_data is not None}]')
        
        balance = float(user_data.balance)

        withdraw_fee = float(config.withdraw_fee_percentage) / 100 * value 
        min_user_balance = float(config.min_user_balance)

        if ( min_user_balance + withdraw_fee + value ) > balance :
            logger.info(f'The user does not have enough balance to withdraw the desired amount ( config.min_user_balance + withdraw_fee + value ) > balance [request_id: {request_id} -user_id: {user_id}]')

            new_data = {
                'status': WithdrawHistoryStatus.FAILED,
                'withdraw_fee_value': withdraw_fee,
                'error_message': 'The user does not have enough balance to withdraw the desired amount (config.min_user_balance + withdraw_fee + value ) > balance',
                'processingـcompletionـtime': datetime.now(),
            }
            update_withdraw_history_by_request_id(request_id, WithdrawHistoryModelForUpdateDataBase(**new_data), db)

            return

        encryted_private_key = get_p_withdraw(db)
        logger.debug(f'db_main_account > get_p_withdraw > response [request_id: {request_id} -result: {encryted_private_key is not None}]')

        private_key = decrypt_private_key(encryted_private_key, self.pk_password, ENV['PRIVATE_KEY_SALT'])

        tx_hash, status, err_msg = self.contract.send_tx(request_id, value, to_address, private_key)

        if tx_hash is None and status == False:

            logger.info(f'Failed Tx  [request_id: {request_id} user_id: {user_id} -err_msg: {err_msg}]')
            new_data = {
                'status': WithdrawHistoryStatus.FAILED,
                'error_message': err_msg,
                'processingـcompletionـtime': datetime.now(),
            }
            update_withdraw_history_by_request_id(request_id, WithdrawHistoryModelForUpdateDataBase(**new_data), db)

            return

        new_data = {
            'tx_hash': tx_hash,
            'withdraw_fee_value': withdraw_fee
        }

        try:
            
            if tx_hash is not None and status == False:
                new_data.update({
                    'status': WithdrawHistoryStatus.FAILED,
                    'error_message': err_msg,
                    'processingـcompletionـtime': datetime.now()
                    })
                
                logger.info(f'Failed Tx  [request_id: {request_id} user_id: {user_id} -error_message: {err_msg}]')
                update_withdraw_history_by_request_id(request_id, WithdrawHistoryModelForUpdateDataBase(**new_data), db)
                return
    
            new_data.update({'status': WithdrawHistoryStatus.SUCCESS, 'processingـcompletionـtime': datetime.now()})
            decrease_balance(user_id, value + withdraw_fee, db, commit=False)
            update_withdraw_history_by_request_id(request_id, WithdrawHistoryModelForUpdateDataBase(**new_data), db, commit=False)
            db.commit()
            
            logger.info(f'Withdraw Successfull [request_id: {request_id} -user_id: {user_id} -tx_hash: {tx_hash}]')

        except Exception as e :
            logger.error(f'Rollback in saving tx [request_id: {request_id} -user_id: {user_id} -exception: {e} -data: {new_data}]')
            db.rollback()

            new_data.update({
                'status': WithdrawHistoryStatus.FAILED,
                'error_message': f'RollBack [{e}]',
                'processingـcompletionـtime': datetime.now()
                })            
            update_withdraw_history_by_request_id(request_id, WithdrawHistoryModelForUpdateDataBase(**new_data), db)

# create celery app
app, withdraw_worker = create_worker_from(WithdrawCeleryTaskImpl)
# _, notifaction_worker = create_worker_from(NotificationCeleryTask)

# start worker
if __name__ == '__main__':
    app.worker_main()

