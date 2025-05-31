"""Tests for the f323c045cc84_load_nyse_data_2 migration."""
import os
from pathlib import Path
import tempfile

import pytest
from alembic import command
from sqlalchemy import text

from .base import MigrationTestBase


class TestLoadNyseData2(MigrationTestBase):
    """Test the second migration that loads additional NYSE data from CSV files."""
    
    @property
    def migration_id(self):
        return 'f323c045cc84'
    
    @property
    def previous_migration_id(self):
        return '6271cbff91e8'  # The previous migration
    
    @pytest.fixture(autouse=True)
    def setup_data_dir(self, monkeypatch, tmp_path):
        """Set up a temporary directory with test data files."""
        # Create a temporary directory structure that matches the expected path
        data_dir = tmp_path / 'Stock Data' / 'd_us_txt' / 'data' / 'daily' / 'us' / 'nyse stocks' / '2'
        data_dir.mkdir(parents=True)
        
        # Create a test CSV file with sample data
        test_data = """<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>,<OPENINT>
GOOGL,1,20230104,093000,90.0,91.5,89.5,91.0,2000,0
GOOGL,1,20230104,093100,91.0,91.8,90.8,91.5,1200,0
AMZN,1,20230104,093000,85.0,86.0,84.5,85.5,1800,0
"""
        test_file = data_dir / 'test_data_2.txt'
        test_file.write_text(test_data)
        
        # Patch the data directory path in the migration
        monkeypatch.setattr(
            'src.migrations.versions.f323c045cc84_load_nyse_data_2.Path',
            lambda *args: data_dir if 'Stock Data' in str(args[0]) else Path(*args)
        )
        
        return data_dir
    
    def test_upgrade_loads_additional_data(self, setup_database, alembic_config):
        """Test that the migration loads additional data from CSV files."""
        connection = setup_database
        
        # Apply previous migrations
        command.upgrade(alembic_config, self.previous_migration_id)
        
        # Get initial row count
        with connection.begin():
            initial_count = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
        
        # Apply our migration that loads additional data
        command.upgrade(alembic_config, self.migration_id)
        
        # Verify data was loaded
        with connection.begin():
            # Check the number of new rows
            result = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
            assert result == initial_count + 3  # 3 new rows in our test data
            
            # Check some sample data from the new migration
            result = connection.execute(
                text("SELECT ticker, open, high, low, close, vol FROM daily WHERE ticker = 'GOOGL'")
            ).fetchall()
            
            assert len(result) == 2
            assert result[0][0] == 'GOOGL'  # ticker
            assert result[0][1] == 90.0     # open
            assert result[0][2] == 91.5     # high
            assert result[0][3] == 89.5     # low
            assert result[0][4] == 91.0     # close
            assert result[0][5] == '2000'    # vol
    
    def test_downgrade_removes_additional_data(self, setup_database, alembic_config):
        """Test that downgrading removes only the additional data."""
        connection = setup_database
        
        # Apply all migrations up to and including our target
        command.upgrade(alembic_config, self.migration_id)
        
        # Get row count before downgrade
        with connection.begin():
            before_downgrade_count = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
        
        # Revert our migration
        command.downgrade(alembic_config, self.previous_migration_id)
        
        # Get row count after downgrade
        with connection.begin():
            after_downgrade_count = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
        
        # Verify that some rows were removed (the ones added by this migration)
        assert after_downgrade_count < before_downgrade_count
        assert after_downgrade_count >= 0  # But not negative
