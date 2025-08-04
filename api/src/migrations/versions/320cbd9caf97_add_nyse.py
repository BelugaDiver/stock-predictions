"""add nyse

Revision ID: 320cbd9caf97
Revises: 
Create Date: 2025-03-19 21:22:46.921170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from models.daily import Daily

# revision identifiers, used by Alembic.
revision: str = '320cbd9caf97'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

Base = automap_base()

def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    Base.prepare(autoload_with=bind)
    Daily.metadata.create_all(bind=bind)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    Base.prepare(autoload_with=bind)
    daily = Base.classes.daily
    op.drop_table(daily.__name__)
    pass
