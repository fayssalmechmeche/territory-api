import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "postgresql://territory_user:territory_pass@localhost:5433/territory_test_db"

from main import app
from database import Base
from dependencies import get_db

TEST_DATABASE_URL = "postgresql://territory_user:territory_pass@localhost:5433/territory_test_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)

def test_create_point_requires_auth(client):
    response = client.post(
        "/points",
        json={
            "name": "Point non autorisé",
            "category": "test",
            "latitude": 48.8584,
            "longitude": 2.2945
        }
    )
    assert response.status_code == 401


def test_get_nonexistent_point_returns_404(client):
    response = client.get("/points/9999")
    assert response.status_code == 404