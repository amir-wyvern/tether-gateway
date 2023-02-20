import celery


class WithdrawCeleryTask(celery.Task):
    name = 'Withdraw_celery_task'

    def run(self, payload):
        """
        place holder method
        """
        pass


class DepositCeleryTask(celery.Task):
    name = 'Deposit_celery_task'

    def run(self, payload):
        """
        place holder method
        """
        pass


class TransferCeleryTask(celery.Task):
    name = 'Transfer_celery_task'

    def run(self, payload):
        """
        place holder method
        """
        pass


class ContractCeleryTask(celery.Task):
    name = 'Contract_celery_task'

    def run(self, payload):
        """
        place holder method
        """
        pass
