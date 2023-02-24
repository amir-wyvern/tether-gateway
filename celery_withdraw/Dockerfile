FROM python:3.8
ADD ./celery_withdraw/requirements.txt /
ADD ./celery_withdraw/main.py /
ADD ./celery_withdraw/ /celery_tasks/
RUN pip3 install -r requirements.txt
ENTRYPOINT celery -A main worker --concurrency=4 --loglevel=info -n withdraw_worker.%h