import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zohal.settings")

celery_app = Celery("Zohal")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "send-merchant-statistics": {
        "task": "apps.transactions.tasks.send_merchant_statistics",
        "schedule": crontab(minute=0, hour=0),
    },
}


@celery_app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
