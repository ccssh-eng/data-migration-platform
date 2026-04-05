import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="function")
def db_engine(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    yield engine
    engine.dispose()
