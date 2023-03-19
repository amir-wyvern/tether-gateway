# 
FROM python:3.9

# 
WORKDIR /app
# 
COPY ./requirements.txt /app

# 
RUN pip install --upgrade -r /app/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# 
COPY ./auth /app/auth
COPY ./db /app/db
COPY ./cache /app/cache
COPY ./celery_tasks /app/celery_tasks
COPY ./router /app/router
COPY ./.env ./main.py ./schemas.py /app

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
