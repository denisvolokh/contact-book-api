from celery import Celery
from celery.schedules import crontab

app_name = "contacts-tasks-app"
broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"
include = ["tasks"]

celery = Celery(app_name, broker=broker_url, backend=result_backend, include=include)


@celery.task
def task_update_contacts() -> None:
    """Recurring background task to update contacts from external API"""
    print("Recurring background task executed")


# Schedule the task to run every minute
celery.conf.beat_schedule = {
    "update-contacts": {
        "task": "tasks.task_update_contacts",
        "schedule": crontab(minute="*"),
    },
}
