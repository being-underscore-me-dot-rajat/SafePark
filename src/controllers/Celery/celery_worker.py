from celery import Celery

celery = Celery(
    'parkingapp',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['controllers.auth']
)