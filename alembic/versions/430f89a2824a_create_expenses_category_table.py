"""create expenses category table

Revision ID: 430f89a2824a
Revises: f644a79eb2ad
Create Date: 2026-08-21 03:47:22.478968

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "430f89a2824a"
down_revision: Union[str, Sequence[str], None] = "f644a79eb2ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the expense category catalogue."""

    op.create_table(
        "expenses_category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Convert the existing PostgreSQL ENUM column to VARCHAR.
    op.alter_column(
        "expenses",
        "category",
        existing_type=sa.Enum(
            "food",
            "beverages",
            "desserts",
            "operation",
            name="expensecategory",
        ),
        type_=sa.String(length=100),
        existing_nullable=True,
        postgresql_using="category::text",
    )

    # The PostgreSQL ENUM is no longer needed.
    op.execute("DROP TYPE expensecategory")

    # Seed the initial catalogue.
    expenses_category = sa.table(
        "expenses_category",
        sa.column("name", sa.String(length=100)),
        sa.column("active", sa.Boolean()),
    )

    op.bulk_insert(
        expenses_category,
        [
            {"name": "food", "active": True},
            {"name": "beverages", "active": True},
            {"name": "desserts", "active": True},
            {"name": "operation", "active": True},
        ],
    )


def downgrade() -> None:
    """Restore the PostgreSQL ENUM and remove the catalogue."""

    # Re-create the PostgreSQL ENUM.
    expensecategory = sa.Enum(
        "food",
        "beverages",
        "desserts",
        "operation",
        name="expensecategory",
    )

    expensecategory.create(op.get_bind(), checkfirst=True)

    # Convert VARCHAR back to the ENUM.
    op.alter_column(
        "expenses",
        "category",
        existing_type=sa.String(length=100),
        type_=expensecategory,
        existing_nullable=True,
        postgresql_using="category::expensecategory",
    )

    op.drop_table("expenses_category")