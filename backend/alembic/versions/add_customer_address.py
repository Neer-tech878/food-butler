"""add customer address fields

Revision ID: add_customer_address
Revises: make_addresses_mandatory
Create Date: 2025-10-11 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_customer_address'
down_revision = 'make_addresses_mandatory'
branch_labels = None
depends_on = None


def upgrade():
    # Add delivery address fields to customers table
    op.add_column('customers', sa.Column('delivery_address', sa.Text(), nullable=True))
    op.add_column('customers', sa.Column('delivery_lat', sa.Numeric(precision=10, scale=7), nullable=True))
    op.add_column('customers', sa.Column('delivery_lng', sa.Numeric(precision=10, scale=7), nullable=True))


def downgrade():
    # Remove delivery address fields from customers table
    op.drop_column('customers', 'delivery_lng')
    op.drop_column('customers', 'delivery_lat')
    op.drop_column('customers', 'delivery_address')
