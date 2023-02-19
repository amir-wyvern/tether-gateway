import sys

sys.path.append('../')

from celery_tasks.tasks import DepositCeleryTask
from celery_tasks.utils import create_worker_from

from web3 import Web3
from web3.exceptions import  TransactionNotFound

# from datetime import datetime ,timezone
from db import db_config
from db.database import get_db
# from fastapi import Depends
import json
from dotenv import dotenv_values

from db.database import get_db
from db.db_deposit_request import get_request_deposit_by_user
from db.db_deposit_history import (
    create_deposit_history,
    get_history_deposit_by_tx_hash
)
from db.db_main_account import get_deposit_address
from db.models import DepositRequestStatus, DepositHistoryStatus
from schemas import DepositHistoryModelForDataBase


config = dotenv_values("celery_deposit/.env")

TRANSFER_HASH = config['TRASNFER_HASH']

class Contract:

    def __init__(self) -> None:

        self.w3 = Web3(Web3.HTTPProvider(config["PROVIDER_1"]))
        abi = config["ABI"]
        abi = abi.replace('\'', '"')
        abi = json.loads(abi)
        self.tether = self.w3.eth.contract(address= config["CONTRACT"], abi= abi)

    def tx_receipt(self, tx_hash):
        
        failed_count_of_req = 0
        while True:
            
            try:
                receipt = self.w3.eth.getTransactionReceipt(tx_hash)
                return receipt

            except TransactionNotFound as e:
                #send notifaction is faild
                #
                print('timeout') 
                return False

            except Exception as e:
                print('exception')
                if failed_count_of_req >= 3:

                    return False # resend to celery beat
                failed_count_of_req += 1

                pass

    def get_tx(self, tx_hash):

        failed_count_of_req = 0
        while True:
            
            try:
                receipt = self.w3.eth.get_transaction(tx_hash) 
                print(receipt)
                
                return receipt
            
            except TransactionNotFound as e:
                #send notifaction is faild
                #
                return False

            except Exception as e:

                if failed_count_of_req >= 3:

                    return False # resend to celery beat
                failed_count_of_req += 1

                pass

    def decode_input(self, data):

        try:
            amount = self.tether.decode_function_input(data)[1]['amount'] / 10**18
            return amount
        except Exception as e:
            # set log
            return False
    
    @staticmethod
    def to_check_sum_address(address):

        return Web3.toChecksumAddress(hex(int(address, 16)))


class DepositCeleryTaskImpl(DepositCeleryTask):

    def __init__(self):

        self.contract = Contract()

    def run(self, payload):
        
        user_id = payload["user_id"]
        tx_hash = payload["tx_hash"]


        db = get_db().__next__()

        config = db_config.get_config(db)

        # print(config.deposit_lock)
        if config.deposit_lock == True:
            # send to notifacion 
            pass
            return
        
        deposit_requests = get_request_deposit_by_user(user_id, db, DepositRequestStatus.WAITING)

        if deposit_requests is None:
            # send to notifaction
            pass
            return
        
        old_history_deposit = get_history_deposit_by_tx_hash(tx_hash, db)

        if old_history_deposit is not None and old_history_deposit.status == DepositHistoryStatus.RECEIVED:
            # send to notifaction
            pass
            return
        
        receipt = self.contract.tx_receipt(tx_hash)

        if not receipt or receipt['status'] == 0 :
            # send to notifaction
            pass
            return
        
        state = False
        for log in receipt['logs']:

            if 'address' in log and \
                log.address == self.contract.tether.address and \
                log.topics[0].hex() == TRANSFER_HASH:
                
                blockNumber = receipt.blockNumber
                from_address=  Contract.to_check_sum_address(log.topics[1].hex())
                to_address = Contract.to_check_sum_address(log.topics[2].hex())

                if to_address != Contract.to_check_sum_address( get_deposit_address(db) ):
                    # set log
                    break

                value = int(log.data, 16)
                state = True

                print(blockNumber,from_address, to_address, value)
                
                break
            
        if state == False:
            # send to notification
            pass
            return
        
        for request in deposit_requests:
            if round(request.value, 2) == round(value, 2):
                data = {
                    'tx_hash': tx_hash,
                    'request_id': request.request_id,
                    'user_id': user_id,
                    'origin_address': from_address ,
                    'destination_address': to_address,
                    'error_message': None,
                    'status': DepositHistoryStatus.RECEIVED,
                    'value': value,
                    'tx_timestamp': int,
                    'timestamp': int
                }
                DepositHistoryModelForDataBase
                create_deposit_history()

            else:
                pass



# create celery app
app, _ = create_worker_from(DepositCeleryTaskImpl)
# _, notifaction_worker = create_worker_from(NotificationCeleryTask)

# start worker
if __name__ == '__main__':
    app.worker_main()

