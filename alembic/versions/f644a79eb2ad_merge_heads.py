"""merge alembic heads

Revision ID: f644a79eb2ad
Revises: 6b03c0a59c80, d4f1a2b3c4e5
Create Date: 2026-08-18 16:17:53

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f644a79eb2ad'
down_revision: Union[str, Sequence[str], None] = ('6b03c0a59c80', 'd4f1a2b3c4e5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This is a merge migration; no schema changes required.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No-op
    pass
