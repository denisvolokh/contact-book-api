import logging
import os

import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL: str = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@database:5432/{os.getenv('POSTGRES_DB')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():  # type: ignore
    """Create a new session for each request.

    Returns:
        SessionLocal: A new session.

    Yields:
        Iterator[SessionLocal]: A new session.
    """

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def check_db_connected() -> None:
    """This function checks if the database is connected.

    Raises:
        e: Exception raised if unable to connect to the database.
    """

    try:
        database = databases.Database(SQLALCHEMY_DATABASE_URL)
        if not database.is_connected:
            await database.connect()
            await database.execute("SELECT 1")
        logger.info("[+] Database is connected!")
    except Exception as e:
        logger.exception("[-] Database is not connected!")
        raise e


async def check_db_disconnected() -> None:
    """This function checks if the database is disconnected.

    Raises:
        e: Exception raised if unable to connect to the database.
    """

    try:
        database = databases.Database(SQLALCHEMY_DATABASE_URL)
        if database.is_connected:
            await database.disconnect()
        logger.info("[+] Database is Disconnected!")
    except Exception as e:
        raise e
