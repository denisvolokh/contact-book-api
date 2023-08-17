import concurrent
import csv
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import requests
from sqlalchemy import inspect
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session
from utils import nimbus
from utils.database import SessionLocal
from utils.models import Contact


def table_exists(table: DeclarativeMeta, session: Session) -> bool:
    """Check if table exists in database

    Args:
        table (DeclarativeMeta): Table to check
        session (Session): SQLAlchemy session

    Returns:
        bool: True if table exists, False otherwise
    """
    inspector = inspect(session.bind)
    return inspector.has_table(table)


def table_has_records(table: DeclarativeMeta, session: Session) -> bool:
    """Check if table has any records

    Args:
        table (DeclarativeMeta): Table to check
        session (Session): SQLAlchemy session

    Returns:
        bool: True if table has records, False otherwise
    """
    return session.query(table).count() > 0


def load_csv_data(filename: str) -> List[Dict[str, str]]:
    """Load data from CSV file

    Args:
        filename (str): Path to CSV file

    Returns:
        List[Dict[str, str]]: List of dictionaries containing data from CSV file
    """

    with open(filename, mode="r") as file:
        csv_reader = csv.DictReader(file)
        return [row for row in csv_reader]


def enrich_contact(contact: Contact, session: requests.Session) -> Contact:
    """Enrich contact with data from Nimbus

    Args:
        contact (Contact): Contact to enrich
        session (requests.Session): HTTP request session

    Returns:
        Contact: Enriched contact, updated nimbus_id field if found
    """

    api = nimbus.NimbusAPIClient(session)

    if contact.email:
        query = {"email": {"is": contact.email}}
        print(f"Searching for contact with email: {contact.email}")

        response: nimbus.NimbusContactsResponse = api.list_contacts(query=query)

        if response and response.meta["total"] > 0:
            contact.nimbus_id = response.resources[0].id
            print(
                f"Found contact with email: {contact.email}, nimbus_id: {contact.nimbus_id}"
            )

    return contact


def import_initial_data() -> None:
    """Perform initial data import from CSV file to database"""
    with SessionLocal() as db_session:
        # if not table_exists(Contact.__table__, db_session):
        #     print("Tables does not exist, skipping data insertion.")
        #     return

        # if table_has_records(Contact, db_session):
        #     print("Tables already has records, skipping data insertion.")
        #     return

        # print("Loading initial data...")

        contacts_data = load_csv_data("data/contacts.csv")

        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for contact_data in contacts_data:
                    contact = Contact(**contact_data)
                    futures.append(executor.submit(enrich_contact, contact, session))

                for future in concurrent.futures.as_completed(futures):
                    enriched_contact = future.result()
                    db_session.add(enriched_contact)

        db_session.commit()
        print("Initial data loaded successfully from CSV files.")


if __name__ == "__main__":
    import_initial_data()
