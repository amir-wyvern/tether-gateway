# from celery_tasks.rabbitmq_config import RABBITMQ_USER, RABBITMQ_PWD, RABBITMQ_HOST, RABBITMQ_PORT
from celery_tasks.redis_config import REDIS_DATABASE, REDIS_HOST, REDIS_PORT
import os

if os.environ.get('REDIS_HOST'):
    REDIS_HOST = os.environ.get('REDIS_HOST')

if os.environ.get('REDIS_PORT'):
    REDIS_PORT = os.environ.get('REDIS_PORT')

if os.environ.get('REDIS_DATABASE'):
    REDIS_DATABASE = os.environ.get('REDIS_DATABASE')

broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}'

result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}'