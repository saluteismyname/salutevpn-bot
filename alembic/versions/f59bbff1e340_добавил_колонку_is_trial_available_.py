"""Добавил раздельные триалы для vless и wireguard и удалил общую колонку

Revision ID: f59bbff1e340
Revises: 5d144f94e9eb
Create Date: 2026-10-27 14:52:51.873485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f59bbff1e340'
down_revision: Union[str, Sequence[str], None] = '5d144f94e9eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Добавляем две новые колонки с дефолтом true
    op.add_column('users', sa.Column('is_trial_available_vless', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('users', sa.Column('is_trial_available_wireguard', sa.Boolean(), server_default='true', nullable=False))
    
    # 2. Если у пользователя уже активен VPN, ставим триалы в false
    op.execute(
        """
        UPDATE users 
        SET is_trial_available_vless = TRUE, 
            is_trial_available_wireguard = TRUE 
        WHERE is_active_vpn = TRUE;
        """
    )
    
    # 3. Удаляем старую общую колонку
    op.drop_column('users', 'is_trial_available')


def downgrade() -> None:
    """Downgrade schema."""
    # Обратный процесс на случай отката
    op.add_column('users', sa.Column('is_trial_available', sa.Boolean(), server_default='true', nullable=False))
    op.drop_column('users', 'is_trial_available_wireguard')
    op.drop_column('users', 'is_trial_available_vless')