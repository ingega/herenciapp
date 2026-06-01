"""adding meat catalogue

Revision ID: da31a2e76bc1
Revises: fb4c4d042aa5
Create Date: 2026-06-01 01:16:07.828824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'da31a2e76bc1'
down_revision: Union[str, Sequence[str], None] = 'fb4c4d042aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
