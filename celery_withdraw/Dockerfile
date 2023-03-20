FROM python:3.9
WORKDIR /withdraw
# 
#COPY ./requirements.txt /app
COPY ./celery_withdraw/pk_security.py ./celery_withdraw/.env ./celery_withdraw/main.py ./celery_withdraw/requirements.txt /withdraw
# ./requirements.txt ./.env ./main.py /withdraw
COPY ../db /withdraw/db
COPY ../celery_tasks /withdraw/celery_tasks
COPY ../cache /withdraw/cache
COPY ../schemas.py /withdraw

#RUN pip install --upgrade -r /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /withdraw/requirements.txt

ENTRYPOINT celery -A main worker --concurrency=4 --loglevel=info -n withdraw_worker.%h
