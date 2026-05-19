"""add_restaurant_admin_fields

Revision ID: ebfecd060fe7
Revises: add_customer_address
Create Date: 2025-10-11 23:22:55.653478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebfecd060fe7'
down_revision: Union[str, Sequence[str], None] = 'add_customer_address'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add restaurant admin fields to restaurants table
    op.add_column('restaurants', sa.Column('address', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('email', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('restaurant_admin_email', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('restaurant_admin_hashed_password', sa.String(), nullable=True))
    
    # Add unique constraint on restaurant_admin_email
    op.create_unique_constraint('uq_restaurant_admin_email', 'restaurants', ['restaurant_admin_email'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraint
    op.drop_constraint('uq_restaurant_admin_email', 'restaurants', type_='unique')
    
    # Remove restaurant admin fields from restaurants table
    op.drop_column('restaurants', 'restaurant_admin_hashed_password')
    op.drop_column('restaurants', 'restaurant_admin_email')
    op.drop_column('restaurants', 'email')
    op.drop_column('restaurants', 'phone')
    op.drop_column('restaurants', 'address')
