"""Tests for the 6271cbff91e8_load_nyse_data migration."""
import os
from pathlib import Path
import tempfile

import pytest
from alembic import command
from sqlalchemy import text

from .base import MigrationTestBase


class TestLoadNyseData(MigrationTestBase):
    """Test the migration that loads NYSE data from CSV files."""
    
    @property
    def migration_id(self):
        return '6271cbff91e8'
    
    @property
    def previous_migration_id(self):
        return '320cbd9caf97'  # The previous migration
    
    @pytest.fixture(autouse=True)
    def setup_data_dir(self, monkeypatch, tmp_path):
        """Set up a temporary directory with test data files."""
        # Create a temporary directory structure that matches the expected path
        data_dir = tmp_path / 'Stock Data' / 'd_us_txt' / 'data' / 'daily' / 'us' / 'nyse stocks' / '1'
        data_dir.mkdir(parents=True)
        
        # Create a test CSV file with sample data
        test_data = """<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>,<OPENINT>
AAPL,1,20230103,093000,125.0,126.5,124.5,126.0,1000,0
AAPL,1,20230103,093100,126.0,126.8,125.8,126.5,800,0
MSFT,1,20230103,093000,240.0,241.0,239.5,240.5,1500,0
"""
        test_file = data_dir / 'test_data.txt'
        test_file.write_text(test_data)
        
        # Patch the data directory path in the migration
        monkeypatch.setattr(
            'src.migrations.versions.6271cbff91e8_load_nyse_data.Path',
            lambda *args: data_dir if 'Stock Data' in str(args[0]) else Path(*args)
        )
        
        return data_dir
    
    def test_upgrade_loads_data(self, setup_database, alembic_config):
        """Test that the migration loads data from CSV files."""
        connection = setup_database
        
        # Apply the initial migration to create the table
        command.upgrade(alembic_config, self.previous_migration_id)
        
        # Apply our migration that loads data
        command.upgrade(alembic_config, self.migration_id)
        
        # Verify data was loaded
        with connection.begin():
            # Check the number of rows
            result = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
            assert result == 3  # 3 rows in our test data
            
            # Check some sample data
            result = connection.execute(
                text("SELECT ticker, open, high, low, close, vol FROM daily WHERE ticker = 'AAPL'")
            ).fetchall()
            
            assert len(result) == 2
            assert result[0][0] == 'AAPL'  # ticker
            assert result[0][1] == 125.0   # open
            assert result[0][2] == 126.5   # high
            assert result[0][3] == 124.5   # low
            assert result[0][4] == 126.0   # close
            assert result[0][5] == '1000'   # vol
    
    def test_downgrade_removes_data(self, setup_database, alembic_config):
        """Test that downgrading removes the loaded data."""
        connection = setup_database
        
        # Apply all migrations up to and including our target
        command.upgrade(alembic_config, self.migration_id)
        
        # Verify data was loaded
        with connection.begin():
            result = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
            assert result > 0
        
        # Revert our migration
        command.downgrade(alembic_config, self.previous_migration_id)
        
        # Verify the table is empty
        with connection.begin():
            result = connection.execute(text("SELECT COUNT(*) FROM daily")).scalar()
            assert result == 0
