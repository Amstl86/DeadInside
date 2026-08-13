"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-08-13 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'items',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('deleted', sa.Boolean(), nullable=True, server_default='0'),
    )


def downgrade():
    op.drop_table('items')
