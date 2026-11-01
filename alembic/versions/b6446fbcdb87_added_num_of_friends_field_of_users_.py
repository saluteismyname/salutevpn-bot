"""added num_of_friends field of users table

Revision ID: b6446fbcdb87
Revises: 36ab887f0004
Create Date: 2026-11-01 05:22:02.604821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6446fbcdb87'
down_revision: Union[str, Sequence[str], None] = '36ab887f0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
