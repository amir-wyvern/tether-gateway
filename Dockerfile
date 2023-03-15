# 
FROM python:3.9

# 
WORKDIR /app

# 
COPY ./requirements.txt /app/requirements.txt

# 
RUN pip install --upgrade -r /app/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY ./auth ./db ./cache ./celery_tasks ./router ./.env ./main.py ./schemas.py /app/

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]