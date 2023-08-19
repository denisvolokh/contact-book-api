import concurrent
import csv
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import requests
from sqlalchemy import inspect
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session

from api.utils import nimbus
from api.utils.database import SessionLocal
from api.utils.models import Contact

logger = logging.getLogger(__name__)


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
        logger.info(f"Searching for contact with email: {contact.email}")

        response: Optional[nimbus.NimbusContactsResponse] = api.list_contacts(
            query=query
        )

        if response and response.meta["total"] > 0:  # type: ignore
            contact.nimbus_id = response.resources[0].id
            logger.info(
                f"Found contact with email: {contact.email}, nimbus_id: {contact.nimbus_id}"
            )

    return contact


async def import_initial_data() -> None:
    """Perform initial data import from CSV files"""

    with SessionLocal() as db_session:
        if not table_exists(Contact.__table__, db_session):
            logger.warning("[!] Tables does not exist, skipping data insertion.")
            return

        if table_has_records(Contact, db_session):
            logger.warning(
                "[!] Tables Contact already has records, skipping data insertion."
            )
            return

        logger.info("[+] Loading initial data...")

        contacts_data = load_csv_data("api/data/contacts.csv")

        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for contact_data in contacts_data:
                    logger.info(f"[+] Loading contact data: {contact_data}")
                    contact = Contact(**contact_data)

                    futures.append(executor.submit(enrich_contact, contact, session))

                for future in concurrent.futures.as_completed(futures):
                    enriched_contact = future.result()
                    db_session.add(enriched_contact)

        db_session.commit()
        logger.info(
            f"[+] Initial data ({len(futures)}) loaded successfully from CSV files."
        )
