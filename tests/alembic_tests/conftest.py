"""Common fixtures for Alembic migration tests."""
import os
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
ALEMBIC_INI = PROJECT_ROOT / "src" / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = PROJECT_ROOT / "src" / "migrations"


def apply_migrations(connection, revision='head'):
    """Apply all alembic migrations up to the specified revision."""
    config = Config(str(ALEMBIC_INI))
    config.set_main_option('script_location', str(ALEMBIC_SCRIPT_LOCATION))
    config.attributes['connection'] = connection
    command.upgrade(config, revision)


def get_revision_id(revision):
    """Get the revision ID from a migration file."""
    migration_path = ALEMBIC_SCRIPT_LOCATION / 'versions' / f"{revision}.py"
    with open(migration_path) as f:
        for line in f:
            if line.startswith('revision = '):
                return line.split('=')[1].strip().strip("'\"")
    raise ValueError(f"Could not find revision in {migration_path}")


@pytest.fixture(scope="module")
def alembic_config():
    """Fixture to configure Alembic for testing."""
    config = Config(str(ALEMBIC_INI))
    config.set_main_option('script_location', str(ALEMBIC_SCRIPT_LOCATION))
    return config


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary SQLite database for testing."""
    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    # Create an engine and connection
    db_url = f"sqlite:///{temp_db.name}"
    engine = create_engine(db_url)
    connection = engine.connect()
    
    # Set up the alembic_version table
    with connection.begin() as trans:
        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        trans.commit()
    
    try:
        yield connection
    finally:
        connection.close()
        os.unlink(temp_db.name)  # Clean up the temporary database file


@pytest.fixture(scope="function")
def setup_database(temp_db, alembic_config):
    """Set up the database with all migrations up to a specific revision."""
    alembic_config.attributes['connection'] = temp_db
    return temp_db
