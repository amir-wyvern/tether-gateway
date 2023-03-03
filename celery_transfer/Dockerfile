FROM python:3.8
ADD ./celery_transfer/requirements.txt /
ADD ./celery_transfer/main.py /
ADD ./celery_transfer/ /celery_tasks/
RUN pip3 install -r requirements.txt
ENTRYPOINT celery -A main worker --concurrency=4 --loglevel=info -n transfer_worker.%h