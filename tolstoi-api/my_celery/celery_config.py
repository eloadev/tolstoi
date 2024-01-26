from celery import Celery

BROKER_URL = 'redis://redis:6379/0'
BACKEND = 'redis://redis:6379/0'
RESULT_BACKEND = 'redis://redis:6379/0'

celery_app = Celery(
    'celery_app',
    broker=BROKER_URL,
    backend=BACKEND,
    result_backend=RESULT_BACKEND
)
