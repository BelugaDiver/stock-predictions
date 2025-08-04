"""Base test class for Alembic migration tests."""
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text


class MigrationTestBase:
    """Base class for testing Alembic migrations."""
    
    @property
    def migration_id(self):
        """The migration ID to test."""
        raise NotImplementedError
    
    @property
    def previous_migration_id(self):
        """The ID of the previous migration."""
        return None
    
    def test_upgrade(self, setup_database, alembic_config):
        """Test that the migration can be applied."""
        connection = setup_database
        
        # Apply all migrations up to the one before our target
        if self.previous_migration_id:
            command.upgrade(alembic_config, self.previous_migration_id)
        
        # Apply our target migration
        command.upgrade(alembic_config, self.migration_id)
        
        # Verify the migration was applied by checking alembic_version
        with connection.begin():
            result = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
            assert result == self.migration_id
    
    def test_downgrade(self, setup_database, alembic_config):
        """Test that the migration can be reverted."""
        connection = setup_database
        
        # Apply all migrations up to our target
        command.upgrade(alembic_config, self.migration_id)
        
        # Revert our target migration
        command.downgrade(
            alembic_config, 
            self.previous_migration_id or 'base'
        )
        
        # If there's a previous migration, check that we reverted to it
        if self.previous_migration_id:
            with connection.begin():
                result = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
                assert result == self.previous_migration_id
        # Otherwise, verify the alembic_version table is empty
        else:
            with connection.begin():
                result = connection.execute(text("SELECT COUNT(*) FROM alembic_version")).scalar()
                assert result == 0
    
    def has_table(self, connection, table_name):
        """Check if a table exists in the database."""
        inspector = inspect(connection)
        return table_name in inspector.get_table_names()
