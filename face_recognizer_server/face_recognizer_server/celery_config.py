from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_recognizer_server.settings_base')

app = Celery()

CELERY_BROKER_URL = 'amqp://recognizer:recognizer@rabbitmq:5672'
CELERY_RESULT_BACKEND = 'amqp://recognizer:recognizer@localhost:5672'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {}

# Use for sequential execution of tasks
CELERY_WORKER_CONCURRENCY = 1
CELERY_QUEUES = (
    Queue('recognizer', Exchange('recognizer'), routing_key='recognizer'),
    Queue('dashboard_statistics', Exchange('dashboard_statistics'), routing_key='dashboard_statistics'),
)
CELERY_DEFAULT_QUEUE = 'recognizer'
CELERY_DEFAULT_EXCHANGE = 'recognizer'
CELERY_DEFAULT_ROUTING_KEY = 'recognizer'
CELERY_ROUTES = {
    # -- HIGH PRIORITY QUEUE -- #
    'stuff.tasks.create_or_update_dataset': {'queue': 'recognizer'}
}

app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    accept_content=CELERY_ACCEPT_CONTENT,
    result_serializer=CELERY_RESULT_SERIALIZER,
    task_serializer=CELERY_TASK_SERIALIZER,
    timezone=CELERY_TIMEZONE,
    beat_schedule=CELERY_BEAT_SCHEDULE,
    worker_concurrency=CELERY_WORKER_CONCURRENCY,
    queues=CELERY_QUEUES,
    default_exchange=CELERY_DEFAULT_EXCHANGE,
    default_routing_key=CELERY_DEFAULT_ROUTING_KEY,
    routes=CELERY_ROUTES
)


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from dashboard.tasks import create_person_statistic_obj_for_yesterday_task
    # Calls create_person_statistic_obj_for_yesterday_task every hour.
    sender.add_periodic_task(crontab(minute=1), create_person_statistic_obj_for_yesterday_task.s(),
                             name='Create person stats for yesterday in different timezones')
