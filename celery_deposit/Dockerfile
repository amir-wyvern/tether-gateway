FROM python:3.9
WORKDIR /deposit
# 
#COPY ./requirements.txt /app
COPY ./celery_deposit/.env ./celery_deposit/main.py ./celery_deposit/requirements.txt /deposit
# ./requirements.txt ./.env ./main.py /deposit
COPY ../db /deposit/db
COPY ../celery_tasks /deposit/celery_tasks
COPY ../cache /deposit/cache
COPY ../schemas.py /deposit

#RUN pip install --upgrade -r /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /deposit/requirements.txt

ENTRYPOINT celery -A main worker --beat --concurrency=4 --loglevel=info -n deposit_worker.%h