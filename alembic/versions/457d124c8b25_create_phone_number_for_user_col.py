"""create phone number for user col

Revision ID: 457d124c8b25
Revises: 85c948e7e263
Create Date: 2022-12-09 14:49:15.772853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '457d124c8b25'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
