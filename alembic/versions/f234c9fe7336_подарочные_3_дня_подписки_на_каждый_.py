"""Подарочные 3 дня подписки на каждый протокол всем пользователям

Revision ID: f234c9fe7336
Revises: cb05c052956f
Create Date: 2026-10-29 14:46:09.238070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f234c9fe7336'
down_revision: Union[str, Sequence[str], None] = 'f59bbff1e340'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET is_trial_available_vless = TRUE,
            is_trial_available_wireguard = TRUE
        WHERE is_active_vpn = TRUE;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET is_trial_available_vless = FALSE,
            is_trial_available_wireguard = FALSE
        WHERE is_active_vpn = TRUE;
        """
    )
