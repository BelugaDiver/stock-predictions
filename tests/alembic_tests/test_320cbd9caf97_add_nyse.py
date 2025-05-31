"""Tests for the 320cbd9caf97_add_nyse migration."""
import pytest
from alembic import command
from sqlalchemy import inspect

from .base import MigrationTestBase


class TestAddNyse(MigrationTestBase):
    """Test the initial migration that creates the daily table."""
    
    @property
    def migration_id(self):
        return '320cbd9caf97'
    
    def test_upgrade_creates_table(self, setup_database, alembic_config):
        """Test that the migration creates the daily table."""
        connection = setup_database
        
        # Verify the table doesn't exist before migration
        assert not self.has_table(connection, 'daily')
        
        # Apply the migration
        command.upgrade(alembic_config, self.migration_id)
        
        # Verify the table exists after migration
        assert self.has_table(connection, 'daily')
        
        # Verify the table has the expected columns
        inspector = inspect(connection)
        columns = [c['name'] for c in inspector.get_columns('daily')]
        expected_columns = [
            'id', 'ticker', 'per', 'date', 'time', 
            'open', 'high', 'low', 'close', 'vol'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Expected column {col} not found in daily table"
    
    def test_downgrade_removes_table(self, setup_database, alembic_config):
        """Test that downgrading removes the daily table."""
        connection = setup_database
        
        # Apply the migration
        command.upgrade(alembic_config, self.migration_id)
        assert self.has_table(connection, 'daily')
        
        # Revert the migration
        command.downgrade(alembic_config, 'base')
        
        # Verify the table was removed
        assert not self.has_table(connection, 'daily')
