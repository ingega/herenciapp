"""fix_order_timestamps_mexico_time

Revision ID: 8bff43b0ef87
Revises: b1a250382aa5
Create Date: 2026-06-16 21:55:20.830084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8bff43b0ef87'
down_revision: Union[str, Sequence[str], None] = 'b1a250382aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
