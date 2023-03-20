FROM python:3.9
WORKDIR /transfer
# 
#COPY ./requirements.txt /app
COPY ./celery_transfer/.env ./celery_transfer/main.py ./celery_transfer/requirements.txt /transfer
# ./requirements.txt ./.env ./main.py /transfer
COPY ../db /transfer/db
COPY ../celery_tasks /transfer/celery_tasks
COPY ../cache /transfer/cache
COPY ../schemas.py /transfer

#RUN pip install --upgrade -r /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /transfer/requirements.txt

ENTRYPOINT celery -A main worker --concurrency=4 --loglevel=info -n transfer_worker.%h
