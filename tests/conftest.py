import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from src.chatbot.db.models import Base
from src.chatbot.db.database import Database
from src.chatbot.api.app import app

pytest_plugins = ['pytest_asyncio']


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator[Database, None, None]:
    # Use in-memory SQLite with check_same_thread=False
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    test_database = Database("sqlite:///:memory:")
    test_database.engine = engine
    test_database.SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    yield test_database

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(test_db: Database) -> Generator[Session, None, None]:
    session = test_db.SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(test_db: Database) -> Generator[TestClient, None, None]:
    from src.chatbot.api.routes import get_db
    from src.chatbot.db.database import db as original_db

    # Override the database instance
    original_engine = original_db.engine
    original_session_local = original_db.SessionLocal

    # Replace with test database
    original_db.engine = test_db.engine
    original_db.SessionLocal = test_db.SessionLocal

    def override_get_db() -> Generator[Session, None, None]:
        session = test_db.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Restore original database
    original_db.engine = original_engine
    original_db.SessionLocal = original_session_local

    app.dependency_overrides.clear()