"""Add missing password and admin columns to customers table

Revision ID: db823a3f6fdc
Revises: 213076a56ed9
Create Date: 2025-10-05 00:52:23.724009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db823a3f6fdc'
down_revision: Union[str, Sequence[str], None] = '213076a56ed9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing columns to customers table (only if they don't exist)
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('customers')]
    
    if 'hashed_password' not in columns:
        op.add_column('customers', sa.Column('hashed_password', sa.String(), nullable=False, server_default=''))
    if 'is_admin' not in columns:
        op.add_column('customers', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the added columns
    op.drop_column('customers', 'is_admin')
    op.drop_column('customers', 'hashed_password')
