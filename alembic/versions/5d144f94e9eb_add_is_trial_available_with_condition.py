"""add_is_trial_available_with_condition

Revision ID: 5d144f94e9eb
Revises: 
Create Date: 2026-10-25 14:50:53.824813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d144f94e9eb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавляем колонку (новые пользователи автоматически получат true)
    op.add_column(
        'users', 
        sa.Column('is_trial_available', sa.Boolean(), server_default='true', nullable=False)
    )
    
    # 2. Переключаем is_trial_available в false для тех, у кого уже есть активные/прошлые даты подписок
    op.execute(
        """
        UPDATE users 
        SET is_trial_available = false 
        WHERE expires_at_vless IS NOT NULL OR expires_at_wireguard IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_column('users', 'is_trial_available')
