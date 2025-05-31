"""load nyse data

Revision ID: 6271cbff91e8
Revises: 320cbd9caf97
Create Date: 2025-03-24 21:37:41.082919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from models.daily import Daily


# revision identifiers, used by Alembic.
revision: str = '6271cbff91e8'
down_revision: Union[str, None] = '320cbd9caf97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.
    
    This migration loads data from CSV files into the daily table.
    The CSV files should be located in the 'data' directory and have the following format:
    ticker,per,date,time,open,high,low,close,vol
    """
    from sqlalchemy.orm import Session
    from pathlib import Path
    import csv
    from datetime import datetime
    from typing import List, Dict
    
    # Get the base directory of the project
    data_dir = Path('F:\Stock Data\d_us_txt\data\daily\us\nyse stocks')
    
    # Ensure data directory exists
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Get all CSV files in the data directory
    csv_files = list(data_dir.glob('*.csv'))
    
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the data directory")
    
    # Create a session
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                # Process each row and create Daily objects
                daily_data = []
                for row in reader:
                    try:
                        # Parse date and time
                        date_str = row['date']
                        time_str = row['time']
                        
                        # Create a unique ID using ticker and datetime
                        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                        unique_id = f"{row['ticker']}_{dt.strftime('%Y%m%d_%H%M%S')}"
                        
                        daily_data.append({
                            'id': unique_id,
                            'ticker': row['ticker'],
                            'per': row['per'],
                            'date_': date_str,
                            'time_': time_str,
                            'open_': float(row['open']),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close_': float(row['close']),
                            'vol': row['vol']
                        })
                    except Exception as e:
                        print(f"Error processing row in {csv_file.name}: {e}")
                        continue
                
                # Bulk insert the data
                if daily_data:
                    op.bulk_insert(
                        sa.table(
                            'daily',
                            sa.column('id', sa.String),
                            sa.column('ticker', sa.String),
                            sa.column('per', sa.String),
                            sa.column('date_', sa.Date),
                            sa.column('time_', sa.Time),
                            sa.column('open_', sa.Float),
                            sa.column('high', sa.Float),
                            sa.column('low', sa.Float),
                            sa.column('close_', sa.Float),
                            sa.column('vol', sa.String)
                        ),
                        daily_data
                    )
                    
                    print(f"Successfully loaded data from {csv_file.name}")
                    
    except Exception as e:
        print(f"Error during data loading: {e}")
        raise
    finally:
        session.close()


def downgrade() -> None:
    """Downgrade schema by removing data loaded from CSV files.
    
    This function will remove all records from the daily table that were
    added during the upgrade process. Since we're using a unique ID format
    that includes the ticker and datetime, we can safely remove all records
    that match this pattern.
    """
    from sqlalchemy.orm import Session
    from pathlib import Path
    import re
    
    # Get the base directory of the project
    base_dir = Path(__file__).parent.parent.parent.parent.parent
    data_dir = base_dir / 'data'
    
    # Create a session
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Get all CSV files in the data directory
        csv_files = list(data_dir.glob('*.csv'))
        
        # Create a regex pattern to match our unique ID format
        # Format: TICKER_YYYYMMDD_HHMMSS
        id_pattern = re.compile(r'^[A-Z]+_\d{8}_\d{6}$')
        
        # Delete records that match our unique ID pattern
        op.execute(
            sa.text("DELETE FROM daily WHERE id ~ :pattern"),
            {'pattern': id_pattern.pattern}
        )
        
        print("Successfully removed data loaded from CSV files")
        
    except Exception as e:
        print(f"Error during data removal: {e}")
        raise
    finally:
        session.close()
