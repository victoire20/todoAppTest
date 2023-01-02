"""add apt num col

Revision ID: 9ac02b06d161
Revises: 0505d7eda4a7
Create Date: 2022-12-09 16:20:13.929737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ac02b06d161'
down_revision = '0505d7eda4a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')
