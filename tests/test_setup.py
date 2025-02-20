from collections import namedtuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from Backend.DB import get_db, Base
from Backend.main import app

# Set up the TestClient
client = TestClient(app)

# Set up the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    setup()
    yield
    teardown()


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db

#
User_ = namedtuple('User_', ['name', 'age', 'user_name'])


def create_test_user(user_name: str, name: str, age: int):
    response = client.post('/users/', json={'user_name': user_name, 'name': name, 'age': age})
    user = User_(name=name, age=age, user_name=response.json()['user_name'])
    return user


def setup() -> None:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)
