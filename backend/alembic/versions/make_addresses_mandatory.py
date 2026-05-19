"""make addresses mandatory

Revision ID: make_addresses_mandatory
Revises: 1d9cf6addc33
Create Date: 2025-10-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_addresses_mandatory'
down_revision = '1d9cf6addc33'
branch_labels = None
depends_on = None


def upgrade():
    # Set default values for existing NULL records before making NOT NULL
    op.execute("UPDATE restaurants SET location = 'Address not provided' WHERE location IS NULL")
    op.execute("UPDATE orders SET delivery_address = 'Address not provided' WHERE delivery_address IS NULL")
    
    # Make restaurant location NOT NULL
    op.alter_column('restaurants', 'location',
               existing_type=sa.String(),
               nullable=False)
    
    # Make order delivery_address NOT NULL
    op.alter_column('orders', 'delivery_address',
               existing_type=sa.Text(),
               nullable=False)


def downgrade():
    # Revert to nullable
    op.alter_column('restaurants', 'location',
               existing_type=sa.String(),
               nullable=True)
    
    op.alter_column('orders', 'delivery_address',
               existing_type=sa.Text(),
               nullable=True)
