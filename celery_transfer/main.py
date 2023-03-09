import sys

sys.path.append('../')

from db.database import get_db
from db import db_config
from db.db_user import get_user, decrease_balance, increase_balance
from db.db_transfer import update_transfer_history_by_request_id

from celery_tasks.tasks import TransferCeleryTask
from celery_tasks.utils import create_worker_from
from schemas import TransferHistoryStatus, TransferHistoryModelForUpdateDataBase

from cache.database import get_redis_cache
from cache.cache_session import (
    set_lock_for_user,
    get_status_lock_from_user,
    unlock_user
)
from datetime import datetime
import logging 


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler to show logs on terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler to save logs to a file
file_handler = logging.FileHandler('transfer_service.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def safe_financial(func):
  
    def wrapper(*args, **kwargs):

        user_id = args[1]['from_user']
        request_id = args[1]['request_id']

        db = get_redis_cache().__next__()

        safe_lock = get_status_lock_from_user(user_id, db) 
        logging.debug(f'cache_session > get_status_lock_from_user > response [request_id: {request_id} -user_id: {user_id} -result: {safe_lock}]')

        if safe_lock == 'True':
            #send again to celery queue
            arg = args[1]
            logger.debug(f'Send again to celery queue [arg: {arg}]')
            transfer_worker.apply_async(args=(arg,), countdown=15)
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


class TransferCeleryTaskImpl(TransferCeleryTask):

    @safe_financial
    def run(self, payload):
        
        logger.debug(f'Receive a task [payload: {payload}]')

        request_id = payload["request_id"]
        from_user = payload["from_user"]
        to_user = payload["to_user"]
        value = payload["value"]

        if from_user == to_user:
            logger.info(f'to_user is same from_user [request_id: {request_id} -user_id: {from_user}]')

            new_data = {
                'error_message': 'to_user is same from_user',
                'status': TransferHistoryStatus.FAILED,
                'processingـcompletionـtime': datetime.now()
            }
            update_transfer_history_by_request_id(request_id, TransferHistoryModelForUpdateDataBase(**new_data), db)
            return 

        db = get_db().__next__()

        config = db_config.get_config(db)
        logger.debug(f'db_config > get_config > response [request_id: {request_id} -result: {config is not None}]')

        if config.transfer_lock == True:
            # send to notifacion 
            logger.info(f'transfer has locked [request_id: {request_id} -user_id: {from_user}]')

            new_data = {
                'error_message': 'transfer has locked',
                'status': TransferHistoryStatus.FAILED,
                'processingـcompletionـtime': datetime.now()
            }
            update_transfer_history_by_request_id(request_id, TransferHistoryModelForUpdateDataBase(**new_data), db)
            return
        
        to_user_data = get_user(from_user, db)

        if to_user_data is None:
            # send to notifacion 
            logger.info(f'The to_user is not exist [request_id: {request_id} -user_id: {from_user} -to_user: {to_user}]')

            new_data = {
                'error_message': 'The to_user is not exist',
                'status': TransferHistoryStatus.FAILED,
                'processingـcompletionـtime': datetime.now()
            }

            update_transfer_history_by_request_id(request_id, TransferHistoryModelForUpdateDataBase(**new_data), db)
            return


        user_data = get_user(from_user, db)
        logger.debug(f'db_user > get_user > response [request_id: {request_id} -result: {user_data is not None}]')


        balance = float(user_data.balance)

        transfer_fee = float(config.transfer_fee_percentage) / 100 * value 
        min_user_balance = float(config.min_user_balance)

        if ( min_user_balance + transfer_fee + value ) > balance :
            # send to notification
            logger.info(f'The user does not have enough balance to transfer the desired amount ( config.min_user_balance + transfer_fee + value ) > balance [request_id: {request_id} -user_id: {from_user}]')
            new_data = {
                'error_message': 'The user does not have enough balance to transfer the desired amount ( config.min_user_balance + transfer_fee + value ) > balance',
                'status': TransferHistoryStatus.FAILED,
                'transfer_fee_value': transfer_fee,
                'processingـcompletionـtime': datetime.now()
            }
            update_transfer_history_by_request_id(request_id, TransferHistoryModelForUpdateDataBase(**new_data), db)
            return

        new_data = {
            'transfer_fee_value': transfer_fee
        }

        try:
            
            new_data.update({
                'status': TransferHistoryStatus.SUCCESS,
                'processingـcompletionـtime': datetime.now()
            })

            decrease_balance(from_user, transfer_fee + value, db, commit=False)
            increase_balance(to_user, value, db, commit=False)
            update_transfer_history_by_request_id(request_id, TransferHistoryModelForUpdateDataBase(**new_data), db, commit=False)
            db.commit()
            
            logger.info(f'Transfer Successfull [request_id: {request_id} -user_id: {from_user} -to_user: {to_user}]')

        except Exception as e :
            logger.error(f'Rollback in saving request [request_id: {request_id} -user_id: {from_user} -exception: {e}]')
            db.rollback()

            new_data.update({
                'error_message': f'RollBack [{e}]',
                'status': TransferHistoryStatus.FAILED,
                'processingـcompletionـtime': datetime.now()
            })
            update_transfer_history_by_request_id(request_id, TransferHistoryModelForUpdateDataBase(**new_data), db)

# create celery app
app, transfer_worker = create_worker_from(TransferCeleryTaskImpl)

# start worker
if __name__ == '__main__':
    app.worker_main()

