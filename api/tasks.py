from concurrent import futures
from typing import List

import requests
from celery import Celery
from celery.schedules import crontab
from utils import crud, models, nimbus
from utils.database import SessionLocal

app_name = "contacts-tasks-app"
broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"
include = ["tasks"]

celery = Celery(app_name, broker=broker_url, backend=result_backend, include=include)


@celery.task
def task_update_contacts() -> None:
    """Recurring background task to update contacts from external API"""
    print("Recurring background task executed")

    with requests.Session() as session:
        nimbus_client = nimbus.NimbusAPIClient(session)

        with SessionLocal() as db_session:
            local_contacts: List[models.Contact] = crud.list_contacts(db_session)

            future_contacts = {}
            with futures.ThreadPoolExecutor(max_workers=10) as executor:
                for local_contact in local_contacts:
                    if local_contact.nimbus_id:
                        future_contacts[
                            executor.submit(
                                nimbus_client.get_contact, local_contact.nimbus_id
                            )
                        ] = local_contact
                    elif local_contact.email:
                        query = {"email": {"is": local_contact.email}}
                        future_contacts[
                            executor.submit(nimbus_client.list_contacts, query)
                        ] = local_contact
                    else:
                        print(
                            f"Local contact {local_contact} does not contain either nimbus_id nor email"
                        )

                for future_contact in futures.as_completed(future_contacts):
                    local_contact = future_contacts[future_contact]
                    data: nimbus.NimbusContactsResponse = future_contact.result()

                    if data and len(data.resources) > 0:
                        remote_contact = data.resources[0]
                        local_contact.nimbus_id = remote_contact["id"]

                        if "first name" in remote_contact.fields and len(
                            remote_contact.fields["first name"] > 0
                        ):
                            local_contact.first_name = remote_contact.fields[
                                "first name"
                            ][0]
                        if "last name" in remote_contact.fields and len(
                            remote_contact.fields["last name"] > 0
                        ):
                            local_contact.last_name = remote_contact.fields[
                                "last name"
                            ][0]
                        if "email" in remote_contact.fields and len(
                            remote_contact.fields["email"] > 0
                        ):
                            local_contact.email = remote_contact.fields["email"][0]


# Schedule the task to run every minute
celery.conf.beat_schedule = {
    "update-contacts": {
        "task": "tasks.task_update_contacts",
        "schedule": crontab(minute="*"),
    },
}
