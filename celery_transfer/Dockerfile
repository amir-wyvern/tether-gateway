FROM python:3.9
WORKDIR /transfer

COPY ./celery_transfer/.env ./celery_transfer/main.py ./celery_transfer/requirements.txt /transfer/
COPY ../db /transfer/db
COPY ../celery_tasks /transfer/celery_tasks
COPY ../cache /transfer/cache
COPY ../schemas.py /transfer

RUN pip install -r /transfer/requirements.txt

CMD ["celery", "-A", "main", "worker", "--concurrency=4", "--loglevel=info", "-n", "transfer_worker.%h"]
