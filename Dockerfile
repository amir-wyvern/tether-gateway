# 
FROM python:3.9

# 
WORKDIR /

# 
COPY ./requirements.txt /

# 
RUN pip install --upgrade -r /requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# 
COPY ./auth ./db ./cache ./celery_tasks ./router ./.env ./main.py ./schemas.py /

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]