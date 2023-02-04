import sys

sys.path.append('../')
sys.path.append('../../')

from time import sleep
from celery_tasks.tasks import DepositCeleryTask, NotificationCeleryTask
from celery_tasks.utils import create_worker_from

from web3 import Web3
from web3.exceptions import TimeExhausted, TransactionNotFound

from datetime import datetime ,timezone
from db import db_deposit_request, db_config
from db.database import get_db
from fastapi import Depends
import json
from dotenv import dotenv_values

config = dotenv_values(".env")

# class Status(str, Enum):
    
#     REQUEST = 'REQUEST' 
#     SUBMIT = 'SUBMIT'

db = get_db().__next__()

class Tools:

    def __init__(self) -> None:

        self.w3 = Web3(Web3.HTTPProvider(config["PROVIDER_1"]))
        abi = config["ABI"]
        abi = abi.replace('\'', '"')
        abi = json.loads(abi)
        self.tether = self.w3.eth.contract(address = config["CONTRACT"], abi = abi)

    def tx_receipt(self, tx_hash):
        
        failed_count_of_req = 0
        while True:
            
            try:
                receipt = self.w3.eth.getTransactionReceipt(tx_hash)
                print('333',receipt)
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
        

    # while True:
    #     try :
    #         break

    #     except RequestsError as e:
            
    #         log.error(f'!! [{accounts_handler.getName(address)}] RequestsError - [{e}]')
    #         utl.get_network(_next= True)
    #         if failed_count_of_req > 3 :
    #             log.info(f'!! [{accounts_handler.getName(address)}] failed tx [{hero_id}, {price}] ')
    #             return False

    #         failed_count_of_req += 1

    #     except RequestsTimeoutError :

    #         log.error(f'!! [{accounts_handler.getName(address)}] RequestsTimeoutError - [{e}]')
    #         utl.get_network(_next= True)
    #         if failed_count_of_req > 3 :
    #             log.info(f'!! [{accounts_handler.getName(address)}] failed tx [{hero_id}, {price}] ')
    #             return False
    
    #         failed_count_of_req += 1

    #     except Exception as e :

    #         log.error(f'!! [{accounts_handler.getName(address)}] error - [{e}]')
    #         utl.get_network(_next= True)
    #         if failed_count_of_req > 3 :
    #             log.info(f'!! [{accounts_handler.getName(address)}] 3 time failed tx [{hero_id}-{price}] ')
    #             return False
            
    #         failed_count_of_req += 1

class DepositCeleryTaskImpl(DepositCeleryTask):

    def __init__(self):

        self.tools = Tools()

    def run(self, payload):
        
        user_id = payload['user_id']
        tx_hash = payload['tx_hash']

        config = db_config.get_config(db)

        print(config.deposit_lock)
        if config.deposit_lock == True:
            # send to notifacion 
            pass
    
        receipt = self.tools.tx_receipt(tx_hash)
        print('\n---------------- receipt ')
        print(receipt)

        if not receipt or receipt['status'] == 0 :
            # send to notifaction
            pass

        tx_data = self.tools.get_tx(tx_hash)
        print('\n---------------- tx data ')
        print(tx_data)

        if 'from' not in tx_data and 'input' not in tx_data :
            # send to notifaction
            pass

        amountTxHash = self.tools.decode_input(tx_data['input'])
        print('\n---------------- amount ')
        print(amountTxHash)
            
        # if lock and lock[0] == False :

        #     """ actual implementation """




        #     if payload['status'] == Status.REQUEST:
                
        #         user_id = payload['user_id']
        #         amount = payload['amount']
        #         origin_address = payload['origin_address']
        #         timestamp = datetime.now(timezone.utc)
                
        #         cursor.execute(f"insert into request_deposits (user_id,origin_address,amount,timestamp) values ({user_id},\'{origin_address}\',{amount},TIMESTAMP \'{timestamp}\');")
        #         conn.commit()

        #     elif payload['status'] == Status.SUBMIT:
                
        #         user_id = payload['user_id']
        #         tx_hash = payload['tx_hash']

        #         try : 
        #             receipt = self.w3.eth.getTransactionReceipt(tx_hash)
        #             if receipt['status']  :
        #                 txInfo = self.w3.eth.get_transaction(tx_hash)
        #                 print( f"2: {'from' in txInfo} {'input' in txInfo }")
        #                 if 'from' in txInfo and 'input' in txInfo :
        #                     try:
        #                         amountTxHash = self.tether.decode_function_input(txInfo['input'])[1]['amount'] / 10**18
        #                     except Exception as e:

        #                         payload = {
        #                             'user_id': user_id,
        #                             'text': ''
        #                         }

        #                         notifaction_worker.apply_async(args=(payload,))
        #                         print('decode functions : ' , e)
                                
        #                         return

                            
        #                     cursor.execute(f"select 1 from deposit_history where tx_hash='{tx_hash}';")
        #                     exist_tx = cursor.fetchone()
        #                     print('exist_tx : ', exist_tx)

        #                     if exist_tx == None:

        #                         cursor.execute(f'select (request_id,user_id,origin_address,amount,timestamp) from request_deposits where user_id={user_id};')
        #                         ls_txs = cursor.fetchall()
        #                         print(ls_txs)
                                
        #                         if ls_txs :
        #                             for tx in ls_txs:
                                        
        #                                 tx = literal_eval(tx[0])
        #                                 amount = tx[3]
        #                                 request_id = tx[0]
                                        
        #                                 if hex(tx[2]).lower() == txInfo['from'].lower() and int(amount) == int(amountTxHash):
        #                                     print('=========')

        #                                     cursor.execute(f"""
        #                                         insert into deposit_history (tx_hash,user_id,origin_address,amount,timestamp) values 
        #                                         (\'{receipt.get('transactionHash').hex()}\',{user_id},\'{receipt.get('from')}\',{amountTxHash},TIMESTAMP \'{datetime.now(timezone.utc)}\');""")   
        #                                     cursor.execute(f"""delete from request_deposits where request_id={request_id} """)
        #                                     conn.commit()
        #                         else:
        #                             print('tx not submit in requests desposit')
                                
        #                     else:
        #                         print('if 2')

        #                 else:
        #                     print('tx invalid')
        #             else :
        #                 print('if 1', receipt['status'] , 'from' in receipt , 'data' in receipt)

        #         except TransactionNotFound as e:
        #             print('TransactionNotFound')

        #         except Exception as e:
        #             print('Exception : ' , e)
                

        #     return True

        # else:
        #     pass


# create celery app
app, _ = create_worker_from(DepositCeleryTaskImpl)
_, notifaction_worker = create_worker_from(NotificationCeleryTask)

# start worker
if __name__ == '__main__':
    app.worker_main()


