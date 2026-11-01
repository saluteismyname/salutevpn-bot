"""added num_of_friends field of users table

Revision ID: a1fb7f93b78b
Revises: 8d5d42c01403
Create Date: 2026-11-01 05:48:28.941474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1fb7f93b78b'
down_revision: Union[str, Sequence[str], None] = '8d5d42c01403'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('num_of_friends', sa.Integer(), server_default='0', nullable=False)
    )


def downgrade() -> None:
    op.drop_column(
        'users',
        'num_of_friends'
    )