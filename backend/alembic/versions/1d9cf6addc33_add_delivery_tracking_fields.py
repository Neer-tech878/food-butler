"""add_delivery_tracking_fields

Revision ID: 1d9cf6addc33
Revises: db823a3f6fdc
Create Date: 2025-10-11 11:54:09.599381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d9cf6addc33'
down_revision: Union[str, Sequence[str], None] = 'db823a3f6fdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add delivery tracking fields to orders table
    op.add_column('orders', sa.Column('delivery_address', sa.Text(), nullable=True))
    op.add_column('orders', sa.Column('delivery_lat', sa.Numeric(precision=10, scale=7), nullable=True))
    op.add_column('orders', sa.Column('delivery_lng', sa.Numeric(precision=10, scale=7), nullable=True))
    op.add_column('orders', sa.Column('driver_lat', sa.Numeric(precision=10, scale=7), nullable=True))
    op.add_column('orders', sa.Column('driver_lng', sa.Numeric(precision=10, scale=7), nullable=True))
    op.add_column('orders', sa.Column('delivery_status', sa.String(), nullable=True, server_default='pending'))
    op.add_column('orders', sa.Column('estimated_delivery_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('driver_name', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('driver_phone', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove delivery tracking fields from orders table
    op.drop_column('orders', 'driver_phone')
    op.drop_column('orders', 'driver_name')
    op.drop_column('orders', 'estimated_delivery_time')
    op.drop_column('orders', 'delivery_status')
    op.drop_column('orders', 'driver_lng')
    op.drop_column('orders', 'driver_lat')
    op.drop_column('orders', 'delivery_lng')
    op.drop_column('orders', 'delivery_lat')
    op.drop_column('orders', 'delivery_address')
