FROM python:3.8
ADD ./celery_deposit/requirements.txt /
ADD ./celery_deposit/main.py /
ADD ./celery_deposit/ /celery_tasks/
RUN pip3 install -r requirements.txt
ENTRYPOINT celery -A main worker --beat --concurrency=4 --loglevel=info -n deposit_worker.%h