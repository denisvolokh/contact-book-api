import os
from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from api.routers.base import api_router
from api.utils import models
from api.utils.database import Base, get_db

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@database:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TEST_DATABASE_URL = (
    SQLALCHEMY_DATABASE_URL
) = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@database:5432/{os.getenv('POSTGRES_TEST_DB')}"
test_engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def start_application():
    app = FastAPI()
    app.include_router(api_router, prefix="/api")
    return app


@pytest.fixture(scope="module")
def app() -> Generator[FastAPI, Any, None]:
    """Fixture to create a FastAPI instance

    Yields:
        Generator[FastAPI, Any, None]: Yields a FastAPI instance
    """

    # Create testdb
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(f"CREATE DATABASE {os.getenv('POSTGRES_TEST_DB')}")

    Base.metadata.create_all(test_engine)
    _app = start_application()

    yield _app

    Base.metadata.drop_all(test_engine)

    # Drop testdb
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(f"DROP DATABASE {os.getenv('POSTGRES_TEST_DB')}")


@pytest.fixture(scope="module")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    """Fixture to create a database session

    Args:
        app (FastAPI): Instance of FastAPI

    Yields:
        Generator[SessionTesting, Any, None]: Yields a database session
    """

    connection = test_engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(
    app: FastAPI, db_session: SessionTesting
) -> Generator[TestClient, Any, None]:
    """Fixture to create a test client with injected database session

    Args:
        app (FastAPI): Instance of FastAPI
        db_session (SessionTesting): Database session

    Yields:
        Generator[TestClient, Any, None]: Yields a test client
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_data(db_session: SessionTesting) -> Generator[None, None, None]:
    """Fixture to load test data

    Args:
        db_session (SessionTesting): Database session

    Yields:
        Generator[None, None, None]: Yields None and cleans up test data after test completes
    """

    test_contact = models.Contact(
        first_name="John",
        last_name="Wick",
        email="john.wick@example.com",
        description="Test Contact",
    )
    db_session.add(test_contact)
    db_session.commit()

    yield

    db_session.delete(test_contact)
    db_session.commit()
