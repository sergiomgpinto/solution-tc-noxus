import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.chatbot.db.models import Base
from src.chatbot.api.app import app


@pytest.fixture
def unique_id():
    """Generate unique ID for test data"""
    return str(uuid.uuid4())[:8]


pytest.current_test_id = str(uuid.uuid4())[:8]


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield SessionLocal()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client
